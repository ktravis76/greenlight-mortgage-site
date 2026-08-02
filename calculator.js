/* Mortgage calculator. Runs entirely in the browser — nothing is sent anywhere,
   which is the point and is what the page promises.

   The rate is a figure the visitor types in to model against. This file contains
   no rate sheet, no lookup, and no default that could be read as an offer. */
(function () {
  'use strict';

  var form = document.getElementById('calc');
  if (!form) return;

  var $ = function (id) { return document.getElementById(id); };

  function num(id) {
    var v = ($(id).value || '').replace(/[^0-9.]/g, '');
    var n = parseFloat(v);
    return isNaN(n) ? 0 : n;
  }

  function money(n) {
    return '$' + Math.round(n).toLocaleString('en-US');
  }

  function pi(principal, annualRate, months) {
    var r = annualRate / 100 / 12;
    if (months <= 0) return 0;
    if (r <= 0) return principal / months;
    return principal * r / (1 - Math.pow(1 + r, -months));
  }

  /* Walk the loan month by month. Returns yearly buckets plus the payoff month,
     so the extra-payment comparison is an actual simulation rather than a
     closed-form approximation that quietly drifts. */
  function schedule(principal, annualRate, months, extra) {
    var r = annualRate / 100 / 12;
    var base = pi(principal, annualRate, months);
    var bal = principal, years = [], m = 0;
    var yi = 0, yp = 0, totalInterest = 0;
    var guard = months + 1200;   // never loop forever on a pathological input

    while (bal > 0.01 && m < guard) {
      var interest = bal * r;
      var principalPart = base - interest + extra;
      if (principalPart <= 0) break;          // payment does not cover interest
      if (principalPart > bal) principalPart = bal;

      bal -= principalPart;
      yi += interest; yp += principalPart; totalInterest += interest;
      m++;

      if (m % 12 === 0 || bal <= 0.01) {
        years.push({ year: Math.ceil(m / 12), interest: yi, principal: yp, balance: bal });
        yi = 0; yp = 0;
      }
    }
    return { years: years, months: m, totalInterest: totalInterest, payment: base };
  }

  function render() {
    var price = num('c-price');
    var down = num('c-down');
    var rate = num('c-rate');
    var termY = parseInt($('c-term').value, 10) || 30;
    var tax = num('c-tax');
    var ins = num('c-ins');
    var extra = num('c-extra');

    var principal = Math.max(price - down, 0);
    var months = termY * 12;

    // No rate, no numbers. The field ships empty on purpose — see the note under
    // it on the page — so until the visitor supplies one there is nothing honest
    // to display.
    if (!(rate > 0)) {
      $('c-total').textContent = '—';
      $('c-breakdown').textContent =
        'Enter a rate above to model against. We do not pre-fill one.';
      document.querySelector('#c-amort tbody').innerHTML =
        '<tr><td colspan="4">Enter an interest rate to see the schedule.</td></tr>';
      $('c-extra-out').textContent = 'Add an amount above to see the effect.';
      return;
    }

    var base = pi(principal, rate, months);
    var monthlyTax = tax / 12;
    var monthlyIns = ins / 12;
    var total = base + monthlyTax + monthlyIns;

    $('c-total').textContent = principal > 0 ? money(total) : '—';
    $('c-breakdown').textContent = principal > 0
      ? money(base) + ' principal & interest · ' + money(monthlyTax) + ' tax · '
        + money(monthlyIns) + ' insurance'
      : 'Enter a home price above the down payment to see a figure.';

    // Amortization table
    var plain = schedule(principal, rate, months, 0);
    var tbody = document.querySelector('#c-amort tbody');
    tbody.innerHTML = plain.years.map(function (y) {
      return '<tr><td>Year ' + y.year + '</td>'
        + '<td class="num">' + money(y.interest) + '</td>'
        + '<td class="num">' + money(y.principal) + '</td>'
        + '<td class="num">' + money(y.balance) + '</td></tr>';
    }).join('');

    // Extra-payment comparison
    var out = $('c-extra-out');
    if (extra > 0 && principal > 0) {
      var withExtra = schedule(principal, rate, months, extra);
      var saved = plain.totalInterest - withExtra.totalInterest;
      var sooner = plain.months - withExtra.months;
      var yrs = Math.floor(sooner / 12), mos = sooner % 12;
      out.innerHTML = 'Paying <strong>' + money(extra) + '</strong> extra each month pays the '
        + 'loan off about <strong>' + (yrs ? yrs + ' year' + (yrs > 1 ? 's' : '') : '')
        + (yrs && mos ? ' and ' : '') + (mos ? mos + ' month' + (mos > 1 ? 's' : '') : '')
        + '</strong> sooner, and saves roughly <strong>' + money(saved)
        + '</strong> in interest over the life of the loan.'
        + '<br><span style="font-size:13px;color:var(--mut)">Estimate only, and it assumes '
        + 'the extra goes to principal every month without fail. Subject to credit approval '
        + 'and underwriting.</span>';
    } else {
      out.textContent = 'Add an amount above to see the effect.';
    }
  }

  form.addEventListener('input', render);
  form.addEventListener('change', render);
  render();
})();
