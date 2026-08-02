/* Shared form handling.
   Any <form data-glm-form="kind"> on the site is picked up here.

   Three rules this file exists to enforce:

   1. Never report success we did not get. If the endpoint is not live or the
      request fails, the visitor is told plainly and given the phone number.
      A fake "thanks!" loses the lead silently, which is worse than an error.
   2. Never send consent metadata from the browser. The consent checkbox state
      travels; the IP, user agent and timestamp are stamped by the Edge Function
      from the real request. A client cannot know its own IP and can lie.
   3. Validate before sending, and announce errors to assistive tech rather
      than only coloring a border red.
*/
(function () {
  'use strict';

  var CFG = window.GLM || {};
  var EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

  function setError(field, on) {
    field.classList.toggle('bad', on);
    var input = field.querySelector('input,select,textarea');
    if (input) input.setAttribute('aria-invalid', on ? 'true' : 'false');
  }

  function validate(form) {
    var ok = true, firstBad = null;
    Array.prototype.forEach.call(form.querySelectorAll('.field'), function (field) {
      var input = field.querySelector('input,select,textarea');
      if (!input || !input.required) return;
      var v = (input.value || '').trim();
      var bad = !v || (input.type === 'email' && !EMAIL.test(v));
      setError(field, bad);
      if (bad) { ok = false; firstBad = firstBad || input; }
    });
    if (firstBad) firstBad.focus();
    return ok;
  }

  function status(form, message, kind) {
    var el = form.querySelector('.formstatus');
    if (!el) return;
    el.textContent = message;
    el.style.marginTop = '16px';
    el.style.fontWeight = '600';
    el.style.fontSize = '15px';
    el.style.color = kind === 'error' ? '#c0392b'
      : kind === 'ok' ? 'var(--g)' : 'var(--mut)';
  }

  function payload(form, kind) {
    var data = { form: kind, page: location.pathname, fields: {} };
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name || el.disabled) return;
      if (el.type === 'checkbox') {
        if (el.checked) data.fields[el.name] = true;
        return;
      }
      if (el.type === 'radio') {
        if (el.checked) data.fields[el.name] = el.value;
        return;
      }
      var v = (el.value || '').trim();
      if (v) data.fields[el.name] = v;
    });

    // The exact consent sentence the visitor saw, captured verbatim so the
    // stored record shows what was actually agreed to rather than whatever the
    // wording happens to be months later.
    var consent = form.querySelector('input[name="tcpa_consent"]');
    if (consent) {
      data.tcpa_consent = consent.checked;
      var label = form.querySelector('label[for="' + consent.id + '"]');
      data.tcpa_consent_text = label ? label.textContent.replace(/\s+/g, ' ').trim() : null;
    }
    // Deliberately absent: consent_ip, consent_ua, consent_at.
    // Those are stamped server-side. See supabase/functions/submit-lead/.
    return data;
  }

  function send(form, kind, btn, label) {
    var body = payload(form, kind);

    function reset() {
      if (!btn) return;
      btn.disabled = false;
      btn.textContent = label;
    }

    if (!CFG.LEAD_ENDPOINT_LIVE) {
      status(form,
        'This form is not connected yet. Please call us on ' + (CFG.PHONE || '903-331-0892') +
        ' — we did not want to show you a thank-you message for something that had not been sent.',
        'error');
      reset();
      return;
    }

    fetch(CFG.LEAD_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'apikey': CFG.SUPABASE_KEY },
      body: JSON.stringify(body),
    }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    }).then(function (result) {
      // The server tells us whether it actually emailed. Pass that through so a
      // page can never promise an email that was not sent.
      form.dispatchEvent(new CustomEvent('glm:sent', {
        bubbles: true, detail: { sent: body, result: result || {} },
      }));
      if (!form.hasAttribute('data-glm-keep')) {
        status(form,
          'Got it. A licensed loan officer will be in touch within one business day.', 'ok');
        form.reset();
      }
      reset();
    }).catch(function () {
      status(form,
        'Something went wrong sending that. Please call us on ' +
        (CFG.PHONE || '903-331-0892') + ' and we will pick it up from there.', 'error');
      reset();
    });
  }

  // Delegated at the document, not bound per form at load. The estimator builds
  // its gate form after this file has already run, and a form that misses the
  // binding submits natively — reloading the page and losing the lead silently.
  // Delegation means any form that appears later is handled the same way.
  document.addEventListener('submit', function (e) {
    var form = e.target.closest('[data-glm-form]');
    if (!form) return;
    e.preventDefault();
    if (!validate(form)) {
      status(form, 'Please check the highlighted fields.', 'error');
      return;
    }
    var btn = form.querySelector('button[type="submit"]');
    var label = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
    status(form, '', '');
    send(form, form.getAttribute('data-glm-form'), btn, label);
  });

  // Clear the error state as soon as the visitor starts fixing it.
  document.addEventListener('input', function (e) {
    var field = e.target.closest && e.target.closest('.field');
    if (field && field.classList.contains('bad')) setError(field, false);
  });
})();
