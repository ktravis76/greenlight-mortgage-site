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
