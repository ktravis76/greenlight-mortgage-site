/* Partner attribution and co-branding.
   ---------------------------------------------------------------------------
   The growth loop this exists to serve:

     a realtor shares a tool link with their buyer
       -> the buyer runs the numbers on our page
       -> the lead reaches Greenlight, attributed to that realtor
       -> the realtor gets credit and a reason to share the next one

   Link shape:
     /tools/affordability?ref=jane-doe&pro=Jane%20Doe&co=Acme%20Realty

     ref  attribution code, stored on the lead in the existing ref_code column
     pro  the person's name, shown on the page
     co   their company, shown on the page

   Attribution has to survive navigation — somebody lands on the affordability
   tool, wanders to /loans/fha, then fills in a form two pages later. So it is
   held in sessionStorage for the visit rather than read off the current URL.

   sessionStorage, not localStorage, and not a cookie: it dies with the tab. A
   referral code is not worth a consent banner, and a stale one attached to a
   lead six weeks later would be worse than no attribution at all. */
(function () {
  'use strict';

  var KEY = 'glm_partner';

  function read() {
    try { return JSON.parse(sessionStorage.getItem(KEY) || 'null'); }
    catch (e) { return null; }
  }

  function clamp(s, n) {
    return (s || '').toString().replace(/[<>]/g, '').trim().slice(0, n);
  }

  // A fresh ?ref= on the URL always wins over whatever is stored, so a second
  // partner's link re-attributes rather than being swallowed by the first.
  var params = new URLSearchParams(location.search);
  var partner = read();

  if (params.get('ref') || params.get('pro')) {
    partner = {
      ref: clamp(params.get('ref'), 64),
      pro: clamp(params.get('pro'), 80),
      co: clamp(params.get('co'), 80),
      landed: location.pathname,
    };
    try { sessionStorage.setItem(KEY, JSON.stringify(partner)); } catch (e) {}
  }

  window.GLM_PARTNER = partner;
  if (!partner) return;

  /* --- co-brand banner ---------------------------------------------------- */
  // Deliberately reads "shared with you by", not "brought to you by". They are
  // sharing a tool, not endorsing a lender, and we should not imply otherwise
  // on their behalf.
  if (partner.pro || partner.co) {
    var who = partner.pro && partner.co ? partner.pro + ' at ' + partner.co
      : (partner.pro || partner.co);
    var bar = document.createElement('div');
    bar.className = 'cobrand';
    bar.innerHTML =
      '<div class="wrap"><span class="cb-label">Shared with you by</span>'
      + '<strong></strong>'
      + '<span class="cb-note">They sent you this tool. It is free to use, and '
      + 'nothing here obliges you to work with anyone.</span></div>';
    bar.querySelector('strong').textContent = who;   // never innerHTML for user input
    var main = document.getElementById('main');
    if (main && main.parentNode) main.parentNode.insertBefore(bar, main);
  }

  /* --- feed the code into every form -------------------------------------- */
  // ref_code already exists on public.leads, so this needs no schema change and
  // the Edge Function already passes it through.
  function tag() {
    if (!partner.ref) return;
    Array.prototype.forEach.call(document.querySelectorAll('[data-glm-form]'), function (form) {
      if (form.elements.ref_code) { form.elements.ref_code.value = partner.ref; return; }
      var input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'ref_code';
      input.value = partner.ref;
      form.appendChild(input);
    });
  }
  tag();

  // The estimator builds its gate form after this file runs, so re-tag when a
  // form appears. Same lesson as the submit handler: anything that assumes the
  // DOM is final at load time will silently miss the one form that matters.
  if ('MutationObserver' in window) {
    new MutationObserver(tag).observe(document.body, { childList: true, subtree: true });
  }

  /* --- keep the code on internal links ------------------------------------ */
  // Belt and braces for anyone who opens a link in a new tab, where
  // sessionStorage does not follow.
  Array.prototype.forEach.call(document.querySelectorAll('a[href^="/"]'), function (a) {
    if (!partner.ref) return;
    if (a.getAttribute('href').indexOf('ref=') > -1) return;
    a.addEventListener('click', function (e) {
      if (!e.metaKey && !e.ctrlKey && e.button === 0) return;   // same tab: storage covers it
      var u = new URL(a.href, location.origin);
      u.searchParams.set('ref', partner.ref);
      if (partner.pro) u.searchParams.set('pro', partner.pro);
      if (partner.co) u.searchParams.set('co', partner.co);
      a.href = u.pathname + u.search;
    });
  });
})();
