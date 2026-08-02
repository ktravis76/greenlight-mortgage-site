/* Share-link builder on /pros.
   A partner types their name, picks a tool, gets a link they can send. */
(function () {
  'use strict';

  var form = document.getElementById('linkbuilder');
  if (!form) return;

  var $ = function (id) { return document.getElementById(id); };
  var out = $('lb-out');
  var status = form.querySelector('.formstatus');

  // Attribution code derived from the name, so a partner never has to be issued
  // one or remember it. Stable for the same name, readable in reporting.
  function slug(s) {
    return (s || '').toLowerCase().normalize('NFKD')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 48);
  }

  function build() {
    var name = $('lb-name').value.trim();
    var co = $('lb-co').value.trim();
    var tool = $('lb-tool').value;
    var ref = slug(name) || slug(co);

    if (!ref) { out.value = ''; return; }

    // Built against the live origin so it works on the preview deploy and on
    // the real domain without anybody editing a constant.
    var u = new URL(tool, location.origin);
    u.searchParams.set('ref', ref);
    if (name) u.searchParams.set('pro', name);
    if (co) u.searchParams.set('co', co);
    out.value = u.toString();
  }

  form.addEventListener('input', build);
  form.addEventListener('change', build);
  build();

  $('lb-copy').addEventListener('click', function () {
    if (!out.value) {
      status.textContent = 'Put your name in first.';
      status.style.color = '#ffd97a';
      return;
    }
    var done = function (ok) {
      status.textContent = ok
        ? 'Copied. Paste it into an email or a text.'
        : 'Could not copy automatically — tap the link above and copy it.';
      status.style.color = ok ? 'var(--go)' : '#ffd97a';
      status.style.fontWeight = '600';
      status.style.marginTop = '14px';
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(out.value).then(function () { done(true); },
        function () { done(false); });
    } else {
      out.select();
      try { done(document.execCommand('copy')); } catch (e) { done(false); }
    }
  });
})();
