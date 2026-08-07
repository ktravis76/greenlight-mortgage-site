/* Greenlight Mortgage — the funnel slider rig.
   One shared component for every /loans/* funnel page. Vanilla JS, no
   dependencies, and everything here is enhancement: with JS off, CSS hides
   the rig and shows a static CTA block instead (.frig-fallback).

   What lives here:
   1. The estimator itself — fat touch sliders driving a big animated number.
      Refi pages model savings; purchase pages model a payment. The math is
      standard amortization and the ONLY rate involved is the sample figure in
      /assets/rates.js, labeled as a sample everywhere it renders.
   2. Analytics — one `funnel_slide` row on first touch, one `funnel_cta` row
      per CTA click, into Supabase analytics_events via the anon key (the same
      publishable key config.js already ships; RLS caps what it can do).
      Meta Pixel: ViewContent on load + custom EstimatorUsed on first touch.
      Deliberately NO `Lead` event — this traffic already converted on
      Facebook's lead form, and double-counting poisons the ad optimization.
   3. The ?src=fb kicker swap, the USDA town picker, and the refi statement
      upload (Supabase Storage `mortgage-statements` + a metadata row — the
      same flow db/2026-08-01-rls-hardening.sql hardened).

   Compliance notes are not decoration: the estimate footnote is rendered by
   the page and never removed here, the output is always called an estimate,
   and nothing in this file writes the word "quote" into the page. */
(function () {
  'use strict';

  var CFG = window.GLM || {};
  var RATES = window.GLM_SAMPLE_RATES || { SAMPLE_RATE: 6.5, SAMPLE_TERM_YEARS: 30, ASSUMED_YEARS_LEFT: 27 };
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var rig = document.querySelector('[data-funnel]');
  // Pages without a rig (tools, blog) still carry the YES flow, so the slug
  // falls back to the path either way.
  var slug = (rig && rig.getAttribute('data-slug'))
    || location.pathname.replace(/\/$/, '').split('/').pop() || 'home';

  /* ------------------------------------------------------------ analytics */
  // A row in analytics_events. Fire-and-forget: analytics must never break
  // the page, block a navigation, or show the visitor an error.
  function track(event, params) {
    try {
      if (!CFG.SUPABASE_URL || !CFG.SUPABASE_KEY) return;
      fetch(CFG.SUPABASE_URL + '/rest/v1/analytics_events', {
        method: 'POST',
        keepalive: true,
        headers: {
          'Content-Type': 'application/json',
          'apikey': CFG.SUPABASE_KEY,
          'Authorization': 'Bearer ' + CFG.SUPABASE_KEY,
          'Prefer': 'return=minimal',
        },
        body: JSON.stringify({ event: event, params: params || {} }),
      }).catch(function () {});
    } catch (e) { /* never let telemetry take the page down */ }
  }

  function pixel() {
    try { if (window.fbq) window.fbq.apply(null, arguments); } catch (e) {}
  }

  /* ------------------------------------------------- ?src=fb kicker swap */
  // Facebook lead-ad traffic gets told, immediately, that the click worked.
  // Organic traffic sees the standard kicker the page shipped with.
  if (/[?&]src=fb\b/.test(location.search)) {
    var kicker = document.querySelector('[data-fb-kicker]');
    if (kicker) kicker.textContent = 'You’re in the right place — here’s what happens next.';
  }

  /* ------------------------------------------ router answers ride along */
  // The /start quizzes hand off with ?from=router&va=yes&goal=lower… (refi)
  // or &mil=…&loc=…&profile=… (buy), plus any UTM tags. Ryan's rule: nobody
  // re-types anything — so those answers are injected into the walk-through
  // form as hidden fields (stored on the lead), the name param prefills the
  // contact forms, and everything is packed into a carry string appended to
  // the application links on success.
  var URL_PARAMS = (function () {
    var out = {};
    location.search.replace(/^\?/, '').split('&').forEach(function (pair) {
      if (!pair) return;
      var i = pair.indexOf('=');
      var k = decodeURIComponent(i < 0 ? pair : pair.slice(0, i));
      var v = decodeURIComponent(i < 0 ? '' : pair.slice(i + 1).replace(/\+/g, ' '));
      // Bounded, boring values only — this string ends up in a lead row.
      if (/^[\w-]{1,32}$/.test(k) && v.length <= 80) out[k] = v;
    });
    return out;
  })();
  var ROUTER_KEYS = ['from', 'va', 'goal', 'age', 'mil', 'loc', 'profile',
                     'src', 'utm_source', 'utm_medium', 'utm_campaign'];

  function injectRouterFields(form) {
    if (!form) return;
    ROUTER_KEYS.forEach(function (k) {
      if (!(k in URL_PARAMS)) return;
      var name = (k === 'from' || k === 'src' || k.indexOf('utm_') === 0) ? k : 'router_' + k;
      if (form.querySelector('input[name="' + name + '"]')) return;
      var input = document.createElement('input');
      input.type = 'hidden';
      input.name = name;
      input.value = URL_PARAMS[k];
      form.appendChild(input);
    });
  }

  function prefillNames() {
    if (!URL_PARAMS.name) return;
    $all('input[name="name"]').forEach(function (el) {
      if (!el.value) el.value = URL_PARAMS.name;
    });
  }

  if (rig || document.querySelector('form[data-yes-form]')) {
    pixel('track', 'ViewContent', { content_name: slug, content_category: 'loan-funnel' });
  }

  /* ------------------------------------------------------------- helpers */
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function money0(n) { return '$' + Math.round(n).toLocaleString('en-US'); }

  // Standard amortization payment: principal, annual rate %, months.
  function pay(principal, rate, months) {
    var r = rate / 100 / 12;
    if (months <= 0) return 0;
    if (r <= 0) return principal / months;
    return principal * r / (1 - Math.pow(1 + r, -months));
  }

  // Remaining balance implied by a payment at a rate over n months (PV of an
  // annuity) — how the refi rig infers a balance the visitor did not enter.
  function balanceFrom(payment, rate, months) {
    var r = rate / 100 / 12;
    if (r <= 0) return payment * months;
    return payment * (1 - Math.pow(1 + r, -months)) / r;
  }

  /* ------------------------------------------------------- the number tween */
  // The output counts toward its new value over ~400ms while the thumb moves.
  // Retargets mid-flight, so dragging feels continuous rather than jumpy.
  function makeCounter(el, fmt) {
    var shown = 0, target = 0, from = 0, t0 = 0, raf = null, started = false;
    function frame(now) {
      var k = Math.min(1, (now - t0) / 400);
      k = 1 - Math.pow(1 - k, 3);                       // ease-out cubic
      shown = from + (target - from) * k;
      el.textContent = fmt(shown);
      if (k < 1) raf = requestAnimationFrame(frame);
      else { shown = target; raf = null; }
    }
    return function set(value, pulseUp) {
      target = value;
      if (reduced || !started) {                        // first paint: no show
        started = true; shown = value; el.textContent = fmt(value);
        return;
      }
      from = shown; t0 = performance.now();
      if (!raf) raf = requestAnimationFrame(frame);
      if (pulseUp) {
        el.classList.remove('pulse');
        void el.offsetWidth;                            // restart the animation
        el.classList.add('pulse');
      }
    };
  }

  /* --------------------------------------------------------- the slider rig */
  function initRig() {
    if (!rig) return;

    // The sample figure renders from rates.js, never from the HTML — one
    // place to change it, and it is always labeled as a sample.
    $all('[data-sample-label]', rig).forEach(function (el) {
      el.textContent = 'The dials model a ' + RATES.SAMPLE_RATE
        + '% sample figure — for illustration only, not today’s pricing and not an offer. '
        + 'Your actual rate will differ.';
    });

    // 'refi' | 'purchase'. Read live, because a dual rig (the homepage) can
    // switch modes with its tabs.
    function mode() { return rig.getAttribute('data-mode'); }
    var out = rig.querySelector('[data-out]');
    var sub = rig.querySelector('[data-out-sub]');
    var live = rig.querySelector('[data-out-live]');    // sr-only, aria-live
    if (!out) return;

    var counter = makeCounter(out, money0);
    var best = -Infinity;                               // pulse only on improvement
    var touched = false;
    var liveTimer = null;

    var sliders = {};
    $all('input[type="range"][data-var]', rig).forEach(function (el) {
      sliders[el.getAttribute('data-var')] = el;
    });

    function val(name, fallback) {
      var el = sliders[name];
      if (!el) return fallback;
      var x = parseFloat(el.value);
      return isNaN(x) ? fallback : x;
    }

    function fmtFor(el) {
      var f = el.getAttribute('data-fmt');
      if (f === 'pct') return function (v) { return v.toFixed(3).replace(/\.?0+$/, '') + '%'; };
      if (f === 'money') return money0;
      return function (v) { return String(v); };
    }

    // Value bubble + track fill for every slider.
    Object.keys(sliders).forEach(function (name) {
      var el = sliders[name];
      var bubble = rig.querySelector('output[data-for="' + name + '"]');
      var fmt = fmtFor(el);
      var paint = function () {
        var min = parseFloat(el.min), max = parseFloat(el.max);
        var pct = max > min ? ((parseFloat(el.value) - min) / (max - min)) * 100 : 0;
        el.style.setProperty('--fill', pct + '%');
        if (bubble) bubble.textContent = fmt(parseFloat(el.value));
      };
      paint();
      el.addEventListener('input', paint);
    });

    // The refi balance slider only participates while its <details> is open.
    var balDetails = rig.querySelector('details[data-balance]');

    function compute() {
      if (mode() === 'refi') {
        var pmt = val('pay', 1850);
        var cur = val('cur', 6.875);
        var months, bal;
        if (balDetails && balDetails.open && sliders.bal) {
          bal = val('bal', 250000);
          // Payment + rate + balance imply how long is left; cap at 30 years.
          var r = cur / 100 / 12;
          if (r > 0 && pmt > bal * r) {
            months = Math.min(360, Math.round(-Math.log(1 - r * bal / pmt) / Math.log(1 + r)));
          } else {
            months = RATES.ASSUMED_YEARS_LEFT * 12;
          }
        } else {
          months = RATES.ASSUMED_YEARS_LEFT * 12;
          bal = balanceFrom(pmt, cur, months);
        }
        // Same remaining term on both sides — the honest comparison. Savings
        // from stretching a balance back out to 30 years is not savings.
        var newPI = pay(bal, RATES.SAMPLE_RATE, months);
        var saving = pmt - newPI;
        return {
          value: Math.max(0, saving),
          betterWhenHigher: true,
          state: { pay: pmt, cur: cur, bal: bal, months: months, saving: Math.max(0, saving) },
          sub: saving > 0
            ? 'That’s ' + money0(saving * 12) + ' a year — ' + money0(saving * 360)
              + ' over 30 years if it held.'
            : 'On these dials the sample math doesn’t beat what you already have. '
              + 'That’s a real answer too — and rates move.',
        };
      }
      // purchase
      var price = val('price', 250000);
      var down = val('down', 0);
      var loan = Math.max(0, price * (1 - down / 100));
      var pi = pay(loan, RATES.SAMPLE_RATE, RATES.SAMPLE_TERM_YEARS * 12);
      return {
        value: pi,
        betterWhenHigher: false,
        state: { price: price, down: down, loan: loan, pi: pi },
        sub: money0(price) + ' home, ' + (down % 1 ? down.toFixed(1) : down) + '% down — a '
          + money0(loan) + ' loan, principal & interest only. Taxes and insurance are on top.',
      };
    }

    /* The YES flow and the recoupment meter both feed off estimator state,
       so a visitor's dials follow them into the form and the 36-month test. */
    var yesForm = document.querySelector('form[data-yes-form]');
    var recoup = document.querySelector('[data-recoup]');

    function fmtPct(v) { return v.toFixed(3).replace(/\.?0+$/, '') + '%'; }

    function syncYes(res) {
      var s = res.state;
      // The shiny button carries their live number.
      $all('[data-yes-amount]').forEach(function (el) {
        el.textContent = money0(res.value);
      });
      // Recap chips: "you told us".
      $all('[data-yes-fact]').forEach(function (el) {
        var k = el.getAttribute('data-yes-fact');
        if (k === 'pay' && s.pay != null) el.textContent = money0(s.pay) + '/mo';
        if (k === 'cur' && s.cur != null) el.textContent = fmtPct(s.cur);
        if (k === 'saving' && s.saving != null) el.textContent = money0(s.saving) + '/mo';
        if (k === 'price' && s.price != null) el.textContent = money0(s.price);
        if (k === 'down' && s.down != null) el.textContent = fmtPct(s.down);
        if (k === 'pi' && s.pi != null) el.textContent = money0(s.pi) + '/mo';
      });
      // Hidden fields on the walk-through form — their dials, submitted with
      // the lead so the loan officer calls already knowing the shape of it.
      if (yesForm) {
        var refiKeys = ['current_payment', 'current_rate', 'mortgage_balance',
                        'estimated_monthly_savings'];
        var buyKeys = ['home_price', 'down_payment_pct', 'estimated_payment'];
        var map = mode() === 'refi'
          ? { current_payment: Math.round(s.pay), current_rate: s.cur,
              mortgage_balance: Math.round(s.bal), estimated_monthly_savings: Math.round(s.saving) }
          : { home_price: Math.round(s.price), down_payment_pct: s.down,
              estimated_payment: Math.round(s.pi) };
        Object.keys(map).forEach(function (name) {
          var input = yesForm.querySelector('input[name="' + name + '"]');
          if (input) input.value = String(map[name]);
        });
        // A dual rig carries both field sets; blank the inactive one so a
        // mode switch never submits stale numbers from the other lane.
        if (rig.hasAttribute('data-dual')) {
          (mode() === 'refi' ? buyKeys : refiKeys).forEach(function (name) {
            var input = yesForm.querySelector('input[name="' + name + '"]');
            if (input) input.value = '';
          });
        }
        // The money button's promise: dials + router answers travel into the
        // application links too, so the handoff carries everything forward.
        updateCarryLinks(map);
      }
      // The 36-month meter (refi only): sample costs vs monthly saving.
      if (recoup && mode() === 'refi') {
        var fee = s.bal * 0.005;                       // VA funding fee, sample
        var costs = (RATES.ASSUMED_REFI_COSTS || 3000) + (recoup.hasAttribute('data-va') ? fee : 0);
        var bar = recoup.querySelector('.recoupbar');
        var months = s.saving > 0 ? costs / s.saving : Infinity;
        var readB = recoup.querySelector('[data-recoup-months]');
        var verdict = recoup.querySelector('[data-recoup-verdict]');
        if (bar) {
          var fill = bar.querySelector('.fill');
          var pct = months === Infinity ? 100 : Math.min(100, (months / 36) * 100);
          if (fill) fill.style.width = pct + '%';
          bar.classList.toggle('over', !(months <= 36));
        }
        if (readB) readB.textContent = months === Infinity ? '—'
          : (months < 1 ? '<1' : String(Math.ceil(months)));
        if (verdict) verdict.textContent = months <= 36
          ? 'On these dials, that clears the VA’s 36-month rule — the math makes sense to run for real.'
          : 'On these dials it doesn’t clear 36 months — and a loan that doesn’t shouldn’t be written. Different numbers, different answer.';
      }
    }

    function render(animate) {
      var res = compute();
      var improved = res.betterWhenHigher ? res.value > best + 0.5 : (best === -Infinity ? false : res.value < best - 0.5);
      best = res.betterWhenHigher ? Math.max(best, res.value) : (best === -Infinity ? res.value : Math.min(best, res.value));
      counter(res.value, animate && improved);
      if (sub) sub.textContent = res.sub;
      syncYes(res);
      // Announce to assistive tech once the dust settles, not every frame.
      if (live) {
        clearTimeout(liveTimer);
        liveTimer = setTimeout(function () {
          live.textContent = (mode() === 'refi' ? 'Estimated monthly savings: ' : 'Estimated monthly payment: ')
            + money0(res.value) + '. ' + res.sub;
        }, 600);
      }
    }

    function firstTouch() {
      if (touched) return;
      touched = true;
      track('funnel_slide', { slug: slug, mode: mode(), page: location.pathname });
      pixel('trackCustom', 'EstimatorUsed', { content_name: slug });
    }

    rig.addEventListener('input', function (e) {
      if (!e.target.matches || !e.target.matches('input[type="range"]')) return;
      firstTouch();
      render(true);
    });
    if (balDetails) balDetails.addEventListener('toggle', function () { render(true); });

    // Dual rig (the homepage): tabs flip data-mode, everything marked
    // data-mode-only follows, and the walk-through form's goal follows too.
    function applyMode() {
      var m = mode();
      $all('[data-mode-only]').forEach(function (el) {
        el.hidden = el.getAttribute('data-mode-only') !== m;
      });
      if (yesForm) {
        var goal = yesForm.querySelector('input[name="goal"]');
        if (goal) goal.value = m === 'refi' ? 'refinance' : 'purchase';
      }
    }
    if (rig.hasAttribute('data-dual')) {
      $all('[data-mode-tab]', rig).forEach(function (btn) {
        btn.addEventListener('click', function () {
          rig.setAttribute('data-mode', btn.getAttribute('data-mode-tab'));
          $all('[data-mode-tab]', rig).forEach(function (b) {
            b.setAttribute('aria-pressed', String(b === btn));
          });
          applyMode();
          best = -Infinity;              // new lane, new baseline — no pulse
          firstTouch();
          render(false);
        });
      });
      applyMode();
    }

    render(false);
  }

  /* ------------------------------------------------------- carry-forward */
  // Append the estimator state + router answers to every [data-carry] link
  // (the application handoffs), so nothing gets re-typed downstream.
  function updateCarryLinks(estimatorMap) {
    var parts = [];
    Object.keys(estimatorMap || {}).forEach(function (k) {
      parts.push(k + '=' + encodeURIComponent(estimatorMap[k]));
    });
    ROUTER_KEYS.forEach(function (k) {
      if (k in URL_PARAMS) parts.push(k + '=' + encodeURIComponent(URL_PARAMS[k]));
    });
    if (!parts.length) return;
    var q = parts.join('&');
    $all('[data-carry]').forEach(function (a) {
      var base = (a.getAttribute('href') || '').split('?')[0];
      if (base) a.href = base + '?' + q;
    });
  }

  /* ------------------------------------------------------- the YES moment */
  // Standalone on purpose: tools and blog pages carry the walk-through form
  // without a slider rig, and the shiny button must still work there.
  function initYes() {
    var yesForm = document.querySelector('form[data-yes-form]');

    // Router answers ride along: into the lead row via hidden fields, into
    // the reach-out forms, and onto the carry links even before any drag.
    injectRouterFields(yesForm);
    $all('form[data-glm-form="funnel_callback"]').forEach(injectRouterFields);
    prefillNames();
    updateCarryLinks({});

    $all('[data-yes-btn]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        track('funnel_cta', { slug: slug, cta: 'yes_click', page: location.pathname });
        pixel('trackCustom', 'EstimatorUsed', { content_name: slug, step: 'yes' });
        var target = document.getElementById('yes');
        if (!target) return;
        target.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
        var first = target.querySelector('input[type="text"],input[type="tel"],input[type="email"]');
        if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, reduced ? 0 : 550);
      });
    });

    // When the walk-through form actually sends (forms.js dispatches
    // glm:sent only on confirmed success), swap the fields for the
    // what-happens-next block. Never on failure — forms.js already shows
    // the phone number, and a fake handoff loses the lead silently.
    if (yesForm) {
      yesForm.addEventListener('glm:sent', function () {
        yesForm.classList.add('yes-done');
        track('funnel_cta', { slug: slug, cta: 'yes_submitted', page: location.pathname });
      });
    }
  }

  /* ------------------------------------------------------- CTA click rows */
  document.addEventListener('click', function (e) {
    var cta = e.target.closest && e.target.closest('[data-funnel-cta]');
    if (!cta) return;
    track('funnel_cta', {
      slug: slug || location.pathname.replace(/\/$/, '').split('/').pop(),
      cta: cta.getAttribute('data-funnel-cta'),
      page: location.pathname,
    });
  });

  /* --------------------------------------------- one page, ONE next action */
  // site.js appends a sticky mobile action bar pointing at /tools/estimate.
  // On a funnel page the one next action is the Big Button, so the bar is
  // retargeted at it instead of sending paid traffic off to a second funnel.
  function retargetActionbar() {
    if (!rig) return;
    var go = document.querySelector('.actionbar .ab-go');
    var big = document.querySelector('[data-big-cta]');
    if (go && big) {
      go.href = big.getAttribute('href') || '#cta';
      go.textContent = big.getAttribute('data-short-label') || big.textContent.replace(/\s+/g, ' ').trim();
      go.setAttribute('data-funnel-cta', 'actionbar');
    }
  }

  /* -------------------------------------------------- USDA town picker */
  // A static list of known-eligible-area names. Deliberately NOT an
  // eligibility API — USDA maps run on exact address, so the page says
  // "likely" and routes to a human for the real check.
  function initTowns() {
    var wrap = document.querySelector('[data-town-picker]');
    if (!wrap) return;
    var outEl = document.querySelector('[data-town-out]');
    wrap.addEventListener('click', function (e) {
      var btn = e.target.closest && e.target.closest('button[data-town]');
      if (!btn) return;
      $all('button[data-town]', wrap).forEach(function (b) {
        b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
      });
      var town = btn.getAttribute('data-town');
      if (outEl) {
        outEl.innerHTML = '<strong>' + town + '?</strong> Likely eligible — homes around '
          + town + ' regularly qualify. USDA runs on your exact address though, '
          + 'so let us check the actual property before you count on it.';
        outEl.classList.remove('pop');
        void outEl.offsetWidth;
        outEl.classList.add('pop');
      }
      track('funnel_slide', { slug: slug, mode: 'town', town: town, page: location.pathname });
      pixel('trackCustom', 'EstimatorUsed', { content_name: slug, town: town });
    });
  }

  /* ------------------------------------------------- statement upload (refi) */
  // The refi Big Button. File goes to the private mortgage-statements bucket,
  // then one metadata row into mortgage_statement_uploads — columns limited to
  // exactly what RLS grants the anon key. lead_id is linked server-side later;
  // the browser never claims one (that is the whole point of the policy).
  var MIMES = {
    'application/pdf': 'pdf', 'image/jpeg': 'jpg', 'image/png': 'png',
    'image/heic': 'heic', 'image/webp': 'webp',
  };
  var EXT_MIME = { pdf: 'application/pdf', jpg: 'image/jpeg', jpeg: 'image/jpeg',
                   png: 'image/png', heic: 'image/heic', webp: 'image/webp' };

  function ownerKey() {
    try {
      var k = localStorage.getItem('glm_owner_key');
      if (!k) {
        k = (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
          : 'k' + Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
        localStorage.setItem('glm_owner_key', k);
      }
      return k;
    } catch (e) { return 'k' + Date.now().toString(36); }
  }

  function initUpload() {
    var box = document.querySelector('[data-statement-upload]');
    if (!box) return;
    var input = box.querySelector('input[type="file"]');
    var btn = box.querySelector('[data-upload-btn]');
    var status = box.querySelector('[data-upload-status]');
    var picked = box.querySelector('[data-upload-picked]');
    if (!input || !btn) return;

    function say(msg, kind) {
      if (!status) return;
      status.textContent = msg;
      status.className = 'fupstatus' + (kind ? ' ' + kind : '');
    }

    input.addEventListener('change', function () {
      var f = input.files && input.files[0];
      if (picked) picked.textContent = f ? f.name : '';
      say('', '');
    });

    btn.addEventListener('click', function () {
      var f = input.files && input.files[0];
      if (!f) { input.click(); return; }

      var mime = f.type;
      if (!mime) {                                      // iPhone HEIC often has no type
        var extGuess = (f.name.split('.').pop() || '').toLowerCase();
        mime = EXT_MIME[extGuess] || '';
      }
      if (!MIMES[mime]) {
        say('That file type won’t work here — send a PDF from your servicer’s site, or a photo (JPG, PNG, HEIC) of the statement.', 'err');
        return;
      }
      if (f.size > 15 * 1024 * 1024) {
        say('That file is over 15MB. A photo of the first page is plenty.', 'err');
        return;
      }

      var path = (slug || 'refi') + '/' + Date.now().toString(36) + '-'
        + Math.random().toString(36).slice(2, 8) + '.' + MIMES[mime];

      btn.disabled = true;
      var label = btn.textContent;
      btn.textContent = 'Sending…';
      say('Sending your statement…', '');

      fetch(CFG.SUPABASE_URL + '/storage/v1/object/mortgage-statements/' + path, {
        method: 'POST',
        headers: {
          'apikey': CFG.SUPABASE_KEY,
          'Authorization': 'Bearer ' + CFG.SUPABASE_KEY,
          'Content-Type': mime,
          'x-upsert': 'false',
        },
        body: f,
      }).then(function (res) {
        if (!res.ok) throw new Error('storage HTTP ' + res.status);
        return fetch(CFG.SUPABASE_URL + '/rest/v1/mortgage_statement_uploads', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'apikey': CFG.SUPABASE_KEY,
            'Authorization': 'Bearer ' + CFG.SUPABASE_KEY,
            'Prefer': 'return=minimal',
          },
          body: JSON.stringify({
            storage_path: path,
            original_filename: (f.name || '').slice(0, 255),
            mime_type: mime,
            source_slug: slug,
            owner_key: ownerKey(),
          }),
        });
      }).then(function (res) {
        if (!res.ok) throw new Error('meta HTTP ' + res.status);
        box.classList.add('done');
        say('Got it. A licensed loan officer runs your real numbers from the statement — usually same day. No robots, no spam, one call.', 'ok');
        btn.textContent = 'Statement sent ✓';
        track('funnel_cta', { slug: slug, cta: 'statement_uploaded', page: location.pathname });
      }).catch(function () {
        // Never fake a success. A silent lost statement is worse than an error.
        btn.disabled = false;
        btn.textContent = label;
        say('That didn’t go through — not your fault. Call ' + (CFG.PHONE || '903-331-0892')
          + ' or try again in a minute.', 'err');
      });
    });
  }

  try {
    initRig();
    initYes();
    initTowns();
    initUpload();
    retargetActionbar();
  } catch (err) {
    // The rig failing must never strand the visitor without a path forward:
    // reveal the no-JS fallback CTA block instead of a dead panel.
    if (rig) rig.classList.add('rig-failed');
    if (window.console) console.error('[greenlight] funnel init failed', err);
  }
})();
