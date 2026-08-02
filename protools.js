/* Partner tools: buyer affordability, seller net proceeds, rent vs buy.
   ---------------------------------------------------------------------------
   All three run entirely in the browser and collect nothing. That is the point:
   a realtor has to be willing to put these in front of their own client, and
   nobody shares a tool that harvests the people they send to it.

   The same rate rule as everywhere else on this site — no field ships with a
   rate pre-filled, and there is no rate sheet in this file. The visitor supplies
   a figure to model against, and the page says so next to the input. An
   affordability number is also never a pre-approval, and every output says that
   too.

   One module per tool, picked by which root element is on the page. */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var money0 = function (n) { return '$' + Math.round(n).toLocaleString('en-US'); };
  function num(id) {
    var el = $(id);
    if (!el) return 0;
    var v = (el.value || '').replace(/[^0-9.]/g, '');
    var n = parseFloat(v);
    return isNaN(n) ? 0 : n;
  }
  function pmt(principal, annualRate, months) {
    var r = annualRate / 100 / 12;
    if (months <= 0) return 0;
    if (r <= 0) return principal / months;
    return principal * r / (1 - Math.pow(1 + r, -months));
  }
  /* Inverse of pmt: what loan does a given monthly payment support? */
  function principalFor(payment, annualRate, months) {
    var r = annualRate / 100 / 12;
    if (months <= 0 || payment <= 0) return 0;
    if (r <= 0) return payment * months;
    return payment * (1 - Math.pow(1 + r, -months)) / r;
  }
  function bind(form, fn) {
    if (!form) return;
    form.addEventListener('input', fn);
    form.addEventListener('change', fn);
    fn();
  }

  /* ==================================================== BUYER AFFORDABILITY */
  // Front-end and back-end ratios are the standard underwriting shape, but the
  // limits are guidance, not guarantees — every lender and program moves them.
  // The output is a RANGE, deliberately. A single precise number invites people
  // to treat it as an approval.
  (function affordability() {
    var form = $('afford');
    if (!form) return;

    bind(form, function () {
      var income = num('af-income');          // gross monthly
      var debts = num('af-debts');            // monthly obligations
      var rate = num('af-rate');
      var years = parseInt(($('af-term') || {}).value, 10) || 30;
      var down = num('af-down');
      var taxRate = num('af-tax') || 1.8;     // % of value per year
      var insYear = num('af-ins') || 2400;
      var hoa = num('af-hoa');

      var out = $('af-out');
      if (!(income > 0) || !(rate > 0)) {
        out.innerHTML = '<p class="cap">Enter your monthly income and a rate to model '
          + 'against.</p>';
        $('af-detail').innerHTML = '';
        return;
      }

      // Two common guardrails. Front-end caps housing cost against income;
      // back-end caps total debt. The binding one is whichever is lower.
      function priceAt(frontPct, backPct) {
        var byFront = income * (frontPct / 100);
        var byBack = income * (backPct / 100) - debts;
        var budget = Math.max(Math.min(byFront, byBack), 0);
        // Strip the non-loan parts of the payment before solving for principal.
        var monthlyIns = insYear / 12;
        var avail = budget - monthlyIns - hoa;
        if (avail <= 0) return 0;
        // Taxes scale with price, so solve iteratively rather than algebraically.
        var price = 0;
        for (var i = 0; i < 40; i++) {
          var monthlyTax = price * (taxRate / 100) / 12;
          var forLoan = avail - monthlyTax;
          if (forLoan <= 0) { price = 0; break; }
          var loan = principalFor(forLoan, rate, years * 12);
          var next = loan + down;
          if (Math.abs(next - price) < 50) { price = next; break; }
          price = next;
        }
        return Math.max(price, 0);
      }

      var conservative = priceAt(28, 36);
      var stretch = priceAt(31, 43);

      if (stretch <= 0) {
        out.innerHTML = '<p class="cap">On these figures the monthly obligations use up the '
          + 'room a lender would look for. That is worth a conversation rather than a '
          + 'conclusion &mdash; there are programs built for exactly this.</p>';
        $('af-detail').innerHTML = '';
        return;
      }

      out.innerHTML =
        '<p class="cap">Estimated price range</p>'
        + '<p class="big">' + money0(conservative) + '&ndash;' + money0(stretch) + '</p>'
        + '<p class="cap">with ' + money0(down) + ' down, modelled at ' + rate + '% over '
        + years + ' years</p>'
        + '<p class="rnote"><strong>An estimate, not a pre-approval and not a commitment to '
        + 'lend.</strong> Subject to credit approval and underwriting. It uses common '
        + 'debt-to-income guidance, but every lender and loan program sets its own limits, '
        + 'and credit, employment history and the property itself all move the answer. Only '
        + 'a licensed loan officer can tell you what you actually qualify for.</p>';

      var housing = Math.min(income * 0.28, income * 0.36 - debts);
      $('af-detail').innerHTML =
        '<div class="tablewrap"><table><tbody>'
        + row('Gross monthly income', money0(income))
        + row('Other monthly debts', money0(debts))
        + row('Housing budget at the conservative end', money0(Math.max(housing, 0)))
        + row('Down payment', money0(down))
        + row('Property tax modelled', taxRate + '% of value per year')
        + row('Insurance modelled', money0(insYear) + ' per year')
        + (hoa ? row('HOA', money0(hoa) + ' per month') : '')
        + '</tbody></table></div>';
    });

    function row(k, v) {
      return '<tr><th>' + k + '</th><td class="num">' + v + '</td></tr>';
    }
  })();

  /* ==================================================== SELLER NET PROCEEDS */
  (function netProceeds() {
    var form = $('netsheet');
    if (!form) return;

    bind(form, function () {
      var price = num('np-price');
      var payoff = num('np-payoff');
      var commissionPct = num('np-commission');
      var closingPct = num('np-closing');
      var repairs = num('np-repairs');
      var concessions = num('np-concessions');
      var other = num('np-other');

      var out = $('np-out');
      if (!(price > 0)) {
        out.innerHTML = '<p class="cap">Enter a sale price to see an estimate.</p>';
        $('np-detail').innerHTML = '';
        return;
      }

      var commission = price * (commissionPct / 100);
      var closing = price * (closingPct / 100);
      var costs = commission + closing + repairs + concessions + other;
      var net = price - payoff - costs;

      out.innerHTML =
        '<p class="cap">Estimated net proceeds</p>'
        + '<p class="big">' + money0(net) + '</p>'
        + '<p class="cap">from a ' + money0(price) + ' sale, after payoff and costs</p>'
        + '<p class="rnote"><strong>An estimate only.</strong> Actual proceeds depend on the '
        + 'final settlement statement, your exact payoff quote on the closing date, prorated '
        + 'taxes, and anything negotiated with the buyer. Your title company produces the '
        + 'figure that matters. We are not attorneys or tax advisers &mdash; talk to yours '
        + 'about the tax treatment of a sale.</p>';

      $('np-detail').innerHTML =
        '<div class="tablewrap"><table><tbody>'
        + r('Sale price', price)
        + r('Mortgage payoff', -payoff)
        + r('Agent commission (' + commissionPct + '%)', -commission)
        + r('Closing costs (' + closingPct + '%)', -closing)
        + (repairs ? r('Repairs', -repairs) : '')
        + (concessions ? r('Buyer concessions', -concessions) : '')
        + (other ? r('Other', -other) : '')
        + '<tr class="total"><th>Estimated net</th><td class="num">' + money0(net)
        + '</td></tr>'
        + '</tbody></table></div>';
    });

    function r(k, v) {
      var cls = v < 0 ? ' style="color:#a3402f"' : '';
      return '<tr><th>' + k + '</th><td class="num"' + cls + '>'
        + (v < 0 ? '&minus;' : '') + money0(Math.abs(v)) + '</td></tr>';
    }
  })();

  /* ========================================================== RENT VS BUY  */
  (function rentVsBuy() {
    var form = $('rvb');
    if (!form) return;

    bind(form, function () {
      var rent = num('rv-rent');
      var rentGrowth = num('rv-rentgrowth') || 3;
      var price = num('rv-price');
      var down = num('rv-down');
      var rate = num('rv-rate');
      var years = parseInt(($('rv-years') || {}).value, 10) || 7;
      var appreciation = num('rv-appreciation') || 3;
      var taxRate = num('rv-tax') || 1.8;
      var insYear = num('rv-ins') || 2400;
      var maintPct = num('rv-maint') || 1;
      var sellCostPct = num('rv-sellcost') || 8;

      var out = $('rv-out');
      if (!(rent > 0) || !(price > 0) || !(rate > 0)) {
        out.innerHTML = '<p class="cap">Enter your rent, a purchase price, and a rate to '
          + 'model against.</p>';
        $('rv-detail').innerHTML = '';
        return;
      }

      var loan = Math.max(price - down, 0);
      var months = 30 * 12;
      var pi = pmt(loan, rate, months);
      var r = rate / 100 / 12;

      // Renting: rent paid over the period, growing each year.
      var rentTotal = 0, curRent = rent;
      for (var y = 0; y < years; y++) {
        rentTotal += curRent * 12;
        curRent *= (1 + rentGrowth / 100);
      }

      // Buying: every dollar out, less every dollar back at sale.
      //
      //   net = (down + all P&I + carrying costs) - (sale value - balance - selling costs)
      //
      // which simplifies to  price + interest + carry + sellCosts - value,
      // because the down payment and the loan together are just the price, and
      // the principal you paid down cancels against the balance you no longer
      // owe. Worth writing out: an earlier version credited the equity back
      // without counting the principal payments as cash out, which quietly
      // understated the cost of buying by the whole principal paid — i.e. it
      // put a thumb on the scale for buying, on a lender's website, on the one
      // page that claims to be honest about when renting wins.
      var bal = loan, carry = 0, interestPaid = 0;
      var value = price;
      for (var m = 0; m < years * 12; m++) {
        var interest = bal * r;
        var principal = pi - interest;
        if (principal < 0) principal = 0;
        bal = Math.max(bal - principal, 0);
        interestPaid += interest;
        carry += (value * (taxRate / 100)) / 12;      // property tax
        carry += insYear / 12;                        // insurance
        carry += (value * (maintPct / 100)) / 12;     // upkeep
        if ((m + 1) % 12 === 0) value *= (1 + appreciation / 100);
      }
      var sellCosts = value * (sellCostPct / 100);
      var equity = value - bal - sellCosts;
      var netBuyCost = price + interestPaid + carry + sellCosts - value;
      var ownCost = interestPaid + carry;

      var better = netBuyCost < rentTotal;
      var diff = Math.abs(rentTotal - netBuyCost);

      out.innerHTML =
        '<p class="cap">Over ' + years + ' years</p>'
        + '<p class="big">' + (better ? 'Buying' : 'Renting') + '</p>'
        + '<p class="cap">comes out roughly ' + money0(diff) + ' ahead on these assumptions</p>'
        + '<p class="rnote"><strong>An illustration, not advice and not a commitment to '
        + 'lend.</strong> It is extremely sensitive to the appreciation and rent-growth '
        + 'figures you chose, and nobody can know those in advance. It ignores the tax '
        + 'treatment of mortgage interest, what you might have earned investing the down '
        + 'payment instead, and the plain fact that moving is expensive and disruptive. '
        + 'Use it to see the shape of the trade-off, not to make the decision.</p>';

      $('rv-detail').innerHTML =
        '<div class="tablewrap"><table><tbody>'
        + row('Total rent paid over ' + years + ' years', money0(rentTotal))
        + row('Monthly principal &amp; interest if you buy', money0(pi))
        + row('Interest, tax, insurance and upkeep paid', money0(ownCost))
        + row('Estimated value after ' + years + ' years', money0(value))
        + row('Loan balance remaining', money0(bal))
        + row('Equity after selling costs', money0(equity))
        + row('Net cost of owning', money0(netBuyCost))
        + '</tbody></table></div>';
    });

    function row(k, v) {
      return '<tr><th>' + k + '</th><td class="num">' + v + '</td></tr>';
    }
  })();
})();

/* ========================================================= VA IRRRL SCREENER */
/* The consumer-facing sibling of the internal VA refi screener.
   ---------------------------------------------------------------------------
   Two levers decide almost every one of these deals, and both came out of the
   27 Jul build session rather than out of a textbook:

   1. THE DISABILITY RATING. A service-connected rating of 10% or more waives
      the VA funding fee entirely. On a $250k balance that is $1,250 of cost
      that simply disappears, and it frequently flips a marginal file into a
      clear one. It is the first question worth asking and it is routinely the
      last one anybody asks.

   2. THE ESCROW REFUND. Borrowers see the new loan amount go up — because the
      new loan funds a new escrow account — and conclude they are borrowing
      more. They are, briefly. Their current servicer refunds the old escrow
      balance, usually within 30 days. It is close to a wash, and not explaining
      it kills deals that were fine.

   The 36-month recoupment test is a real VA requirement, not a rule of thumb:
   costs have to be recovered by the monthly saving inside 36 months. This tool
   applies it honestly and says so when a file fails, because a lender's
   calculator that never says "don't do this" is a brochure. */
(function irrrl() {
  var form = document.getElementById('irrrl');
  if (!form) return;

  var $ = function (i) { return document.getElementById(i); };
  var m0 = function (n) { return '$' + Math.round(n).toLocaleString('en-US'); };

  function n(id) {
    var el = $(id); if (!el) return 0;
    var v = (el.value || '').replace(/[^0-9.]/g, '');
    var x = parseFloat(v); return isNaN(x) ? 0 : x;
  }
  function pay(p, rate, months) {
    var r = rate / 100 / 12;
    if (months <= 0) return 0;
    if (r <= 0) return p / months;
    return p * r / (1 - Math.pow(1 + r, -months));
  }

  function render() {
    var bal = n('ir-balance');
    var cur = n('ir-rate');
    var yrsLeft = parseFloat(($('ir-left') || {}).value || 27);
    var nw = n('ir-new');
    var costs = n('ir-costs');
    var waived = ($('ir-disability') || {}).value === 'Yes, 10% or higher';
    var out = $('ir-out');

    if (!(bal > 0) || !(cur > 0) || !(nw > 0)) {
      out.innerHTML = '<p class="cap">Fill in your balance, your current rate, and a rate '
        + 'to model against.</p>';
      $('ir-detail').innerHTML = '';
      return;
    }

    // IRRRL funding fee is 0.5% of the loan amount, waived at a 10%+
    // service-connected disability rating.
    var fee = waived ? 0 : bal * 0.005;
    var totalCosts = fee + costs;

    var months = Math.round(yrsLeft * 12);
    var curPI = pay(bal, cur, months);
    // Costs are commonly financed into the new loan on an IRRRL.
    var newPI = pay(bal + totalCosts, nw, months);
    var saving = curPI - newPI;

    if (saving <= 0) {
      out.innerHTML =
        '<p class="cap">On these numbers</p>'
        + '<p class="big" style="font-size:clamp(30px,5vw,44px)">Not yet</p>'
        + '<p class="cap">the rate you entered does not beat what you already have once '
        + 'costs are included</p>'
        + '<p class="rnote">That is worth knowing, and we would rather tell you than not. '
        + 'Rates move — it may be worth checking again later. Estimate only, not a quote or '
        + 'an approval, and not a commitment to lend.</p>';
      $('ir-detail').innerHTML = '';
      return;
    }

    var recoup = totalCosts / saving;                 // months to break even
    var passes = recoup <= 36;

    out.innerHTML =
      '<p class="cap">Estimated monthly saving</p>'
      + '<p class="big">' + m0(saving) + '</p>'
      + '<p class="cap">and it takes about <strong>' + Math.ceil(recoup)
      + ' months</strong> to recover the costs</p>'
      + '<p class="rnote"><strong>' + (passes
        ? 'That clears the VA 36-month recoupment test.'
        : 'That does NOT clear the VA 36-month recoupment test.')
      + '</strong> ' + (passes
        ? 'VA requires the costs of an IRRRL to be recovered inside 36 months. On these '
          + 'figures this one does, which is the threshold the loan has to meet.'
        : 'VA requires the costs to be recovered inside 36 months, and on these figures they '
          + 'are not. A lender cannot write it as it stands. Lower costs or a bigger rate '
          + 'drop would change that.')
      + ' Estimate only, from figures you entered — not a quote, an approval, or a '
      + 'commitment to lend. Subject to credit approval and underwriting.</p>';

    var rows =
      row('Current principal &amp; interest', m0(curPI))
      + row('New principal &amp; interest', m0(newPI))
      + row('VA funding fee', waived
          ? '<strong style="color:var(--g)">$0 &mdash; waived</strong>'
          : m0(fee) + ' (0.5%)')
      + row('Other closing costs', m0(costs))
      + row('Total cost to do it', m0(totalCosts))
      + row('Months to break even', Math.ceil(recoup) + ' of 36 allowed')
      + row('Saved over the remaining ' + Math.round(yrsLeft) + ' years',
            m0(saving * months - totalCosts));

    var flag = waived
      ? '<div class="callout"><h3>Your funding fee is waived</h3><p>A service-connected '
        + 'disability rating of 10% or more removes the VA funding fee entirely. On this '
        + 'balance that is ' + m0(bal * 0.005) + ' you are not paying, and it is the single '
        + 'biggest reason these deals work for rated veterans.</p></div>'
      : '<div class="callout"><h3>Do you have a disability rating?</h3><p>A '
        + 'service-connected rating of <strong>10% or higher</strong> waives the VA funding '
        + 'fee completely &mdash; ' + m0(bal * 0.005) + ' on this balance. If you are rated '
        + 'and have not told us, change the answer above and watch the number move. A lot of '
        + 'veterans do not realise this applies to them.</p></div>';

    $('ir-detail').innerHTML =
      '<div class="tablewrap"><table><tbody>' + rows + '</tbody></table></div>'
      + flag
      + '<div class="callout"><h3>About the escrow</h3><p>Your new loan amount will look '
      + 'higher than your balance, because the new loan sets up a new escrow account for '
      + 'taxes and insurance. Your current servicer then refunds the escrow you have already '
      + 'built up, usually within about 30 days of closing. It is close to a wash. This trips '
      + 'people up constantly, so it is worth saying plainly.</p></div>';
  }

  function row(k, v) {
    return '<tr><th>' + k + '</th><td class="num">' + v + '</td></tr>';
  }

  form.addEventListener('input', render);
  form.addEventListener('change', render);
  render();
})();
