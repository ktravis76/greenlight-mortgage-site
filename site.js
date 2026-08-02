/* Greenlight Mortgage — site chrome.
   Everything here is enhancement. With JS off the page is complete and navigable:
   the drawer markup is real links, the dropdowns open on :hover/:focus-within in
   CSS, and nothing is hidden behind a script. */
(function () {
  'use strict';

  // If anything in here throws, drop the .js class so the CSS stops hiding
  // .reveal blocks. A broken script must never cost us page content.
  try { main(); } catch (err) {
    document.documentElement.classList.remove('js');
    if (window.console) console.error('[greenlight] chrome init failed', err);
  }

  function main() {

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- sticky header state ------------------------------------------------ */
  var header = document.getElementById('siteheader');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* --- mobile drawer ------------------------------------------------------ */
  var burger = document.querySelector('.burger');
  var drawer = document.querySelector('.drawer');
  if (burger && drawer) {
    var setDrawer = function (open) {
      burger.setAttribute('aria-expanded', String(open));
      drawer.hidden = !open;
      document.body.style.overflow = open ? 'hidden' : '';
    };
    burger.addEventListener('click', function () {
      setDrawer(burger.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') {
        setDrawer(false);
        burger.focus();
      }
    });
    // Reset when we cross back to the desktop nav, so the drawer can't be
    // left open-but-invisible and trap the page scroll.
    window.matchMedia('(min-width:1081px)').addEventListener('change', function (e) {
      if (e.matches) setDrawer(false);
    });
  }

  /* --- dropdown menus: keyboard + touch ----------------------------------- */
  // CSS already handles hover and focus-within. This adds an explicit click
  // toggle so the trigger works on touch and for keyboard users who expect
  // Enter/Space to open a menu rather than tab into it.
  Array.prototype.forEach.call(document.querySelectorAll('.has-menu'), function (wrap) {
    var btn = wrap.querySelector('.navlink');
    var menu = wrap.querySelector('.menu');
    if (!btn || !menu) return;

    var open = function (state) {
      btn.setAttribute('aria-expanded', String(state));
      menu.style.opacity = state ? '1' : '';
      menu.style.visibility = state ? 'visible' : '';
      menu.style.transform = state ? 'none' : '';
    };
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var isOpen = btn.getAttribute('aria-expanded') === 'true';
      Array.prototype.forEach.call(document.querySelectorAll('.has-menu .navlink'),
        function (b) { b.setAttribute('aria-expanded', 'false'); });
      open(!isOpen);
    });
    wrap.addEventListener('mouseleave', function () { open(false); });
    wrap.addEventListener('focusout', function (e) {
      if (!wrap.contains(e.relatedTarget)) open(false);
    });
    wrap.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { open(false); btn.focus(); }
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-menu')) {
      Array.prototype.forEach.call(document.querySelectorAll('.has-menu .menu'),
        function (m) { m.style.opacity = ''; m.style.visibility = ''; m.style.transform = ''; });
      Array.prototype.forEach.call(document.querySelectorAll('.has-menu .navlink'),
        function (b) { b.setAttribute('aria-expanded', 'false'); });
    }
  });

  /* --- scroll reveal ------------------------------------------------------ */
  // Opt-in per element via .reveal. Anything above the fold is never marked,
  // so there is no flash of hidden content on load.
  var targets = document.querySelectorAll('.reveal');
  if (!targets.length) return;
  if (reduced || !('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add('revealed'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('revealed');
      io.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
  Array.prototype.forEach.call(targets, function (el) { io.observe(el); });

  } // main
})();

/* Sticky mobile action bar.
   Appears once the header CTA has scrolled out of reach, hides again at the top
   of the page, and gets out of the way while somebody is typing into a form —
   a fixed bar covering the field you are filling in is worse than no bar. */
(function () {
  'use strict';
  if (window.matchMedia('(min-width:761px)').matches) return;

  var phone = (window.GLM && window.GLM.PHONE) || '903-331-0892';
  var bar = document.createElement('div');
  bar.className = 'actionbar';
  bar.innerHTML =
    '<a class="ab-call" href="tel:' + phone.replace(/[^0-9]/g, '') + '">'
    + '<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true">'
    + '<path d="M3 1.5h2.2l1.1 3-1.5 1.1a9 9 0 0 0 4.6 4.6l1.1-1.5 3 1.1V12a2.5 2.5 0 0 1-2.6 '
    + '2.5A11.6 11.6 0 0 1 1.5 4.1 2.5 2.5 0 0 1 3 1.5z" fill="currentColor"/></svg>Call</a>'
    + '<a class="ab-go" href="/tools/estimate">See what you could save</a>';
  document.body.appendChild(bar);
  document.body.classList.add('has-actionbar');

  var typing = false;
  document.addEventListener('focusin', function (e) {
    if (e.target.closest && e.target.closest('input,textarea,select')) {
      typing = true; bar.classList.remove('up');
    }
  });
  document.addEventListener('focusout', function () {
    typing = false; setTimeout(update, 120);
  });

  function update() {
    if (typing) return;
    bar.classList.toggle('up', window.scrollY > 520);
  }
  update();
  window.addEventListener('scroll', update, { passive: true });
})();
