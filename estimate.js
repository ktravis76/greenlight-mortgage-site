/* Estimated Savings — the consumer-facing refinance estimator.
   ---------------------------------------------------------------------------
   Naming: this is never a "quote" on any consumer surface. Only a licensed loan
   officer can quote, after a real application. Internally the team calls it a
   soft quote; the visitor sees "Estimated Savings".

   What it will NOT do, deliberately:

   - It does not state, imply, or look up a rate Greenlight would offer. Every
     number below is arithmetic on figures the visitor typed, against rate
     reductions labelled on screen as illustrative scenarios. There is no rate
     sheet in this file and there should never be one.
   - It does not keep the visitor's remaining term at 30 years to flatter the
     result. The comparison holds the remaining term constant, which is the
     conservative reading and the honest one.
   - It does not surprise anyone with the gate. The ask is stated on the intro
     screen before question one.
*/
(function () {
  'use strict';

  var root = document.getElementById('estimator');
  if (!root) return;

  var CFG = window.GLM || {};
  var state = { step: 0, answers: {}, result: null };

  var STEPS = [
    {
      key: 'goal', legend: 'What are you hoping to change?',
      help: 'There is no wrong answer here — it just tells us what to look at first.',
      type: 'choice', options: [
        ['payment', 'Lower my monthly payment', 'The most common reason people call.'],
        ['term', 'Pay it off sooner', 'A shorter term costs more per month and far less overall.'],
        ['cash', 'Use some of my equity', 'For a renovation, or to clear higher-interest debt.'],
        ['unsure', 'I am not sure yet', 'Perfectly reasonable. We will show you the options.'],
      ],
    },
    {
      key: 'veteran', legend: 'Have you served in the military?',
      help: 'Veterans and service members often have options nobody has explained to them.',
      type: 'choice', options: [
        ['yes', 'Yes', 'Veteran, active duty, Guard or Reserve.'],
        ['spouse', 'I am a surviving spouse', 'You may have VA eligibility too.'],
        ['no', 'No', ''],
      ],
    },
    {
      key: 'balance', legend: 'Roughly how much do you still owe?',
      help: 'An estimate is fine. Nobody is holding you to it.',
      type: 'money', placeholder: '250,000', min: 10000, max: 10000000,
    },
    {
      key: 'rate', legend: 'What rate are you paying now?',
      help: 'It is on your mortgage statement. If you are not sure, your best guess works.',
      type: 'rate', placeholder: '7.25', min: 0.5, max: 20,
    },
    {
      key: 'years', legend: 'Roughly how many years are left on it?',
      type: 'choice', options: [
        ['27', 'About 25–30 years', 'A recent purchase or refinance.'],
        ['20', 'About 20 years', ''],
        ['15', 'About 15 years', ''],
        ['8', '10 years or fewer', 'Refinancing gets harder to justify this late.'],
      ],
    },
    {
      key: 'payment', legend: 'What is your principal and interest payment?',
      help: 'Optional. Just the loan portion — not taxes or insurance. Skip it and we will '
          + 'work it out from the numbers above.',
      type: 'money', placeholder: '1,700', min: 0, max: 100000, optional: true,
    },
  ];

  // Illustrative scenarios. NOT rates we offer, and labelled as such on screen.
  var DELTAS = [0.5, 1.0, 1.5];

  /* ------------------------------------------------------------------ math */

  function pi(principal, annualRate, years) {
    var r = annualRate / 100 / 12;
    var n = Math.round(years * 12);
    if (n <= 0) return 0;
    if (r <= 0) return principal / n;
    return principal * r / (1 - Math.pow(1 + r, -n));
  }

  function money(n) {
    return '$' + Math.round(n).toLocaleString('en-US');
  }

  function compute(a) {
    var balance = a.balance, rate = a.rate, years = parseFloat(a.years || 27);
    var current = a.payment && a.payment > 0 ? a.payment : pi(balance, rate, years);

    var rows = DELTAS.map(function (d) {
      var newRate = Math.max(rate - d, 0.5);
      var newPi = pi(balance, newRate, years);
      return {
        delta: d,
        monthly: Math.max(current - newPi, 0),
        overTerm: Math.max(current - newPi, 0) * years * 12,
      };
    }).filter(function (r) { return r.monthly > 0; });

    return {
      current: current,
      rows: rows,
      low: rows.length ? rows[0].monthly : 0,
      high: rows.length ? rows[rows.length - 1].monthly : 0,
      years: years,
      veteran: a.veteran === 'yes' || a.veteran === 'spouse',
    };
  }

  /* ----------------------------------------------------------------- views */

  function el(html) {
    var d = document.createElement('div');
    d.innerHTML = html.trim();
    return d.firstElementChild;
  }

  function progress() {
    var pct = Math.round((state.step / STEPS.length) * 100);
    return '<div class="estprog"><div class="estbar" style="width:' + pct + '%"></div>'
      + '<span>Question ' + Math.min(state.step + 1, STEPS.length)
      + ' of ' + STEPS.length + '</span></div>';
  }

  function renderIntro() {
    root.innerHTML = ''
      + '<div class="estcard">'
      + '<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Estimated Savings</p>'
      + '<h2>Six questions, about two minutes.</h2>'
      + '<p class="sub">You will get an estimate on screen at the end — no phone call needed '
      + 'to see it, and no hard credit pull to run it.</p>'
      + '<div class="callout" style="margin:26px 0">'
      + '<h3>So you know before you start</h3>'
      + '<p>To show you the result we ask for your <strong>name, email and phone</strong> at '
      + 'the end. Three fields, nothing else — no address, no employer, no Social Security '
      + 'number. We would rather tell you that now than spring it on you after you have done '
      + 'the work.</p></div>'
      + '<button class="btn go lg" id="est-start">Start &mdash; it takes two minutes</button>'
      + '<p class="disclose">This tool produces an <strong>estimate</strong>, not a quote, an '
      + 'offer of credit, or an approval. It is not a commitment to lend. Any loan is subject '
      + 'to credit approval and underwriting. Rate quotes and eligibility decisions are made '
      + 'only by a licensed loan officer following a complete application.</p>'
      + '</div>';
    root.querySelector('#est-start').addEventListener('click', function () {
      state.step = 0;
      renderStep();
    });
  }

  function renderStep() {
    var s = STEPS[state.step];
    var inner;

    if (s.type === 'choice') {
      inner = '<div class="choices' + (s.options.length > 3 ? ' two' : '') + '">'
        + s.options.map(function (o, i) {
          return '<label class="choice"><input type="radio" name="' + s.key + '" value="'
            + o[0] + '"' + (state.answers[s.key] === o[0] ? ' checked' : '')
            + (i === 0 ? '' : '') + '><span>' + o[1]
            + (o[2] ? '<small>' + o[2] + '</small>' : '') + '</span></label>';
        }).join('') + '</div>';
    } else {
      var val = state.answers[s.key] != null ? state.answers[s.key] : '';
      var prefix = s.type === 'money' ? '$' : '';
      var suffix = s.type === 'rate' ? '%' : '';
      inner = '<div class="field estinput">'
        + (prefix ? '<span class="affix">' + prefix + '</span>' : '')
        + '<input type="text" inputmode="decimal" id="est-val" value="' + val
        + '" placeholder="' + s.placeholder + '" autocomplete="off"'
        + ' aria-label="' + s.legend.replace(/"/g, '') + '">'
        + (suffix ? '<span class="affix right">' + suffix + '</span>' : '')
        + '<p class="err">Please enter a number, or go back a step.</p></div>';
    }

    root.innerHTML = '<div class="estcard">' + progress()
      + '<h2 class="estq">' + s.legend + '</h2>'
      + (s.help ? '<p class="sub">' + s.help + '</p>' : '')
      + inner
      + '<div class="estnav">'
      + (state.step > 0 ? '<button class="btn ghost" id="est-back">Back</button>' : '<span></span>')
      + '<button class="btn go" id="est-next">'
      + (state.step === STEPS.length - 1 ? 'See my estimate' : 'Next') + '</button>'
      + '</div></div>';

    var next = root.querySelector('#est-next');
    var back = root.querySelector('#est-back');
    if (back) back.addEventListener('click', function () { state.step--; renderStep(); });

    if (s.type === 'choice') {
      Array.prototype.forEach.call(root.querySelectorAll('input[type=radio]'), function (r) {
        r.addEventListener('change', function () {
          state.answers[s.key] = r.value;
          advance();
        });
      });
    } else {
      var input = root.querySelector('#est-val');
      input.focus();
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); next.click(); }
      });
    }

    next.addEventListener('click', function () {
      if (s.type === 'choice') {
        if (!state.answers[s.key]) {
          var f = root.querySelector('.choices');
          f.style.outline = '2px solid #c0392b';
          f.style.outlineOffset = '6px';
          f.style.borderRadius = '12px';
          return;
        }
        advance();
        return;
      }
      var raw = root.querySelector('#est-val').value.replace(/[^0-9.]/g, '');
      var n = parseFloat(raw);
      if (!raw && s.optional) { delete state.answers[s.key]; advance(); return; }
      if (isNaN(n) || n < s.min || n > s.max) {
        root.querySelector('.field').classList.add('bad');
        return;
      }
      state.answers[s.key] = n;
      advance();
    });
  }

  function advance() {
    if (state.step < STEPS.length - 1) { state.step++; renderStep(); }
    else { state.result = compute(state.answers); renderGate(); }
  }

  /* ------------------------------------------------------------------ gate */
  // Asked at the end, after the work is done, exactly as promised on the intro.
  // Three fields. Consent is a separate, un-ticked box, and leaving it unticked
  // still shows the result — it is not a condition of anything.

  function renderGate() {
    root.innerHTML = ''
      + '<div class="estcard">'
      + '<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Last step</p>'
      + '<h2>Where should we send it?</h2>'
      + '<p class="sub">Your estimate is ready. Three fields and it is on the next screen — '
      + 'we will email you a copy too, so you are not digging through your inbox for something '
      + 'you just filled in a form to get.</p>'
      + '<form id="est-form" data-glm-form="estimate" data-glm-keep novalidate style="margin-top:26px">'
      + '<div class="field"><label for="e-name">Name</label>'
      + '<input id="e-name" name="name" type="text" autocomplete="name" required maxlength="120">'
      + '<p class="err">Please tell us your name.</p></div>'
      + '<div class="frow">'
      + '<div class="field"><label for="e-email">Email</label>'
      + '<input id="e-email" name="email" type="email" autocomplete="email" required maxlength="254">'
      + '<p class="err">Please enter a valid email address.</p></div>'
      + '<div class="field"><label for="e-phone">Phone</label>'
      + '<input id="e-phone" name="phone" type="tel" autocomplete="tel" required maxlength="32">'
      + '<p class="err">Please enter a phone number.</p></div>'
      + '</div>'
      + '<div class="consent"><input type="checkbox" id="e-tcpa" name="tcpa_consent" value="yes">'
      + '<label for="e-tcpa">' + (window.GLM_TCPA_TEXT || '') + '</label></div>'
      + '<p class="disclose">Leaving that box unticked does not hide your estimate and does not '
      + 'affect any loan. We will simply email you instead of calling.</p>'
      + '<div class="cta"><button class="btn go lg" type="submit">Show me the estimate</button></div>'
      + '<p class="formstatus" role="status" aria-live="polite"></p>'
      + '</form></div>';

    var form = root.querySelector('#est-form');

    // Attach the computed figures so the Edge Function can store them on the
    // lead and put them in the email.
    ['estimated_monthly_savings', 'goal', 'veteran', 'mortgage_balance',
     'current_rate', 'current_payment'].forEach(function (name) {
      var input = document.createElement('input');
      input.type = 'hidden';
      input.name = name;
      form.appendChild(input);
    });
    form.elements.estimated_monthly_savings.value = Math.round(state.result.high);
    form.elements.goal.value = state.answers.goal || '';
    form.elements.veteran.value = state.answers.veteran || '';
    form.elements.mortgage_balance.value = state.answers.balance || '';
    form.elements.current_rate.value = state.answers.rate || '';
    form.elements.current_payment.value = Math.round(state.result.current);

    // The result is shown whether or not the send succeeded — they did the work
    // and they were promised the number. But we tell them the truth about the
    // email either way rather than claiming it is on its way when it is not.
    form.addEventListener('glm:sent', function (e) {
      renderResult(!!(e.detail && e.detail.result && e.detail.result.emailed));
    });
    form.addEventListener('submit', function () {
      if (!CFG.LEAD_ENDPOINT_LIVE) {
        setTimeout(function () { renderResult(false); }, 250);
      }
    });
  }

  /* ---------------------------------------------------------------- result */

  function renderResult(sent) {
    var r = state.result;
    var rows = r.rows.map(function (row) {
      return '<tr><td>' + row.delta.toFixed(2) + ' percentage points lower</td>'
        + '<td class="num">' + money(row.monthly) + ' / month</td>'
        + '<td class="num">' + money(row.overTerm) + '</td></tr>';
    }).join('');

    var vet = r.veteran
      ? '<div class="callout"><h3>Ask about the VA IRRRL</h3><p>You told us you have served. '
        + 'If your current loan is already a VA loan, the Interest Rate Reduction Refinance '
        + 'Loan is a streamlined route with less paperwork than a full refinance. VA rules '
        + 'require it to produce a real benefit and for the costs to recoup within 36 months — '
        + 'a standard worth applying to any refinance, not just a VA one.</p></div>'
      : '';

    // `sent` is the server's own report of whether the email went out. If it did
    // not, say so — a promise of an email that never arrives is worse than no
    // promise. The estimate itself is on screen either way; they earned it.
    var emailLine = sent
      ? 'A copy is on its way to your inbox, and a licensed loan officer will follow up within '
        + 'one business day. Once — not six times in an hour.'
      : 'Your details reached us and a licensed loan officer will follow up within one '
        + 'business day. We could not email you a copy just now, so save this screen or call '
        + (CFG.PHONE || '903-331-0892') + ' if you want it sent over.';

    root.innerHTML = ''
      + '<div class="result">'
      + '<p class="cap">Estimated monthly savings</p>'
      + '<p class="big">' + money(r.low) + '&ndash;' + money(r.high) + '</p>'
      + '<p class="cap">based on the ' + money(r.current)
      + ' principal and interest payment you described, over the same remaining term</p>'
      + '<p class="rnote"><strong>This is an estimate, not a quote, an offer of credit, or an '
      + 'approval, and it is not a commitment to lend.</strong> Subject to credit approval and '
      + 'underwriting. The reductions below are illustrative scenarios for comparison — they '
      + 'are not rates Greenlight is offering you. Your actual options depend on your credit, '
      + 'income, property and the market on the day, and only a licensed loan officer can quote '
      + 'them after a complete application.</p>'
      + '</div>'

      + '<div class="estcard" style="margin-top:22px">'
      + '<h2>What each scenario looks like</h2>'
      + '<p class="sub">Holding your remaining term at about ' + Math.round(r.years)
      + ' years, rather than restarting the clock at 30. Restarting lowers the payment more and '
      + 'usually costs you more overall — we would rather show you the conservative version.</p>'
      + '<div class="tablewrap"><table><thead><tr><th>Illustrative scenario</th>'
      + '<th>Estimated saving</th><th>Over the remaining term</th></tr></thead>'
      + '<tbody>' + (rows || '<tr><td colspan="3">At the rate you are paying now, a refinance '
      + 'may not save you anything. That is worth knowing, and we will tell you so plainly.</td></tr>')
      + '</tbody></table></div>'
      + '<p class="disclose">Estimates only. Subject to credit approval and underwriting. '
      + 'Excludes closing costs, taxes, insurance and mortgage insurance, all of which affect '
      + 'whether refinancing is actually worth doing.</p>'
      + vet
      + '<div class="callout"><h3>What happens next</h3><p>' + emailLine + '</p></div>'
      + '<div class="cta"><a class="btn go" href="' + (window.GLM_APPLY || '#') + '">'
      + 'Start an application</a>'
      + '<a class="btn ghost" href="/contact">Ask a question first</a></div>'
      + '</div>';

    root.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  renderIntro();
})();
