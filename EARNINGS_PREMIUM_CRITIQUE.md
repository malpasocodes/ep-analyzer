# The Earnings Premium Is a Blunt Instrument: Why the One Big Beautiful Bill's Accountability Metric Needs Serious Refinement

*An evidence-based critique of the earnings premium test for higher education accountability*

---

## The Policy at a Glance

Beginning July 2026, under the One Big Beautiful Bill Act, every degree program at every college and university receiving federal financial aid must pass an "earnings premium" (EP) test. The test is straightforward: the median earnings of a program's graduates must exceed the median earnings of high school graduates aged 25–34 in the same state. Programs that fail in two out of three consecutive years lose eligibility for federal student loans.

The premise is intuitive. If a college degree doesn't lift your earnings above a high school diploma, what was the point? But intuitive is not the same as sound. The earnings premium, as currently designed, is a crude metric dressed up as precision. It confounds geography with quality, collapses enormous economic variation into a single number, and commits well-known statistical fallacies. If we're going to tie billions of dollars in federal aid — and the futures of millions of students — to a metric, that metric had better be rigorous. This one isn't.

---

## Problem 1: The Geographic Fallacy — Punishing Place, Not Quality

The EP test compares graduate earnings against **statewide** median earnings for high school graduates. This design choice embeds a geographic fallacy at the very foundation of the metric.

Consider the data. Using Census ACS county-level earnings for high school graduates (table B20004), we find:

- **County-level HS earnings range from $9,814 to $88,493** — a **9-to-1 ratio**
- **Statewide thresholds range from $27,362 to $37,850** — a mere **1.4-to-1 ratio**
- The standard deviation of county earnings ($6,763) is **2.8 times** the standard deviation across state thresholds ($2,428)

The statewide threshold crushes this variation into a single number. A college in rural Appalachian North Carolina must clear the same bar as a college in the Research Triangle — even though local HS earnings differ by tens of thousands of dollars. A community college in Toppenish, Washington, located on the Yakama Indian Reservation, produces graduates who earn $11,000 more than the local 60th percentile. Under local benchmarks, it passes easily. Under the statewide threshold — inflated by Seattle-Tacoma metropolitan earnings — it fails.

This isn't hypothetical. Research from the [University of Wisconsin-Madison](https://lrc.sstar.wisc.edu/documents/SSTAR_ROI_report.pdf) and the Postsecondary Value Commission found that **754 institutions — 16% of all U.S. colleges — would fail the statewide test but pass using local earnings**. These institutions are disproportionately:

- **Public** institutions with broad-access missions
- Serving **high shares of Pell Grant recipients**
- Located in **rural and lower-income communities**

In other words, the statewide benchmark systematically penalizes the institutions most deeply embedded in the communities that need them most. These programs are penalized for their *geography*, not their *quality*.

### The Masking Problem

The geographic distortion cuts both ways. A statewide benchmark doesn't just create false failures — it also creates **false passes**. Institutions in high-cost metros can clear the statewide threshold while producing graduates who earn *less* than local high school graduates. Our analysis shows this "pass state, fail local" pattern is actually the dominant form of divergence. Statewide benchmarks systematically mask local underperformance. This asymmetry — failing rural schools that add value, passing urban schools that don't — is itself the core finding.

---

## Problem 2: The Ecological Fallacy — Comparing Apples to Averages

The EP test commits a textbook [ecological fallacy](https://en.wikipedia.org/wiki/Ecological_fallacy): it draws conclusions about individual programs from aggregate-level data. Specifically:

- **Graduate earnings** are measured at the program-cohort level (sometimes as few as 30–40 completers)
- **The benchmark** is drawn from statewide population-level data (millions of working adults)

These are fundamentally different statistical objects. You cannot meaningfully compare a small cohort's median against a population median and treat the result as a pass/fail quality signal. The benchmark absorbs demographic composition, industrial mix, urbanization patterns, age distributions, and regional labor market conditions that have nothing to do with whether a specific program added educational value.

This is aggregation bias in its purest form. The relationship between education and earnings at the county level is different from the relationship at the state level, which is different from the individual level. Collapsing all of this into a single statewide comparison doesn't simplify the measurement — it distorts it.

---

## Problem 3: Simpson's Paradox in Earnings Data

The EP test is vulnerable to [Simpson's paradox](https://en.wikipedia.org/wiki/Simpson%27s_paradox): a pattern that appears in aggregated data can reverse when the data is disaggregated.

Consider a state with a booming urban core and a depressed rural interior. The statewide median HS earnings are pulled up by urban workers. A rural college's graduates might earn more than *every local comparison group* — more than local HS grads, more than local associate degree holders — but still fall below the statewide median. The aggregate comparison says "fail." The disaggregated reality says "clear success."

This isn't a theoretical curiosity. The earnings data itself demonstrates the reversal. The SF Fed has [documented](https://www.frbsf.org/research-and-insights/publications/economic-letter/2023/08/falling-college-wage-premiums-by-race-and-ethnicity/) that the college wage premium has been falling, but when disaggregated by race and ethnicity, the picture changes entirely. [Andrew Gelman's analysis](https://statmodeling.stat.columbia.edu/2021/03/29/estimating-the-college-wealth-premium-not-so-easy/) showed that when workers were ranked by percentile, lesser-educated workers had *higher* earnings growth — the exact opposite of the aggregate pattern. When your metric is susceptible to reversals under disaggregation, it cannot be trusted as a binary pass/fail gate.

---

## Problem 4: Measurement Error Compounds the Problem

Multiple layers of measurement error make the EP test even less reliable:

### Age-Band Mismatch
The Census ACS B20004 data used for HS earnings benchmarks covers workers aged **25 and older**. The EP test is supposed to evaluate outcomes for *recent* graduates. Older workers have had decades of wage growth, promotions, and career development. Using their earnings as the benchmark inflates the bar that young graduates must clear. This is comparing experienced workers' earnings against career starters' earnings and calling it a fair test.

### Timing Sensitivity
The College Scorecard measures earnings at 6 and 10 years post-enrollment. Our analysis shows that some programs look like failures at 6 years but successes at 10 years. If the EP test catches a program during its graduates' early-career phase, it penalizes a *timing issue*, not a *quality issue*. Nursing graduates, teachers, social workers, and other public-service professionals often have suppressed early earnings that grow substantially over time.

### Institution vs. Program Granularity
The current available data measures earnings at the *institution* level. The actual EP test will be applied at the *program* level. Institution-level data represents a best-case scenario — programs with the weakest earnings outcomes are averaged away by stronger programs. Program-level data will almost certainly reveal more failures, not fewer.

### The Threshold Cliff
**699 institutions** sit within +/-10% of their state threshold. **377 institutions** are within +/-5%. These institutions are one bad cohort, one recession, one measurement revision away from flipping between pass and fail. A metric with a binary pass/fail cutoff and no confidence interval treats a 0.1% miss the same as a 50% miss. In no serious statistical application would we use a point estimate without acknowledging its uncertainty — yet that is precisely what the EP test does.

---

## Problem 5: What the Metric Doesn't Measure

The earnings premium captures one narrow dimension of educational value. It ignores:

- **Cost of living adjustments**: $35,000 in rural Mississippi has far greater purchasing power than $45,000 in Manhattan. The EP test treats both the same.
- **Non-monetary returns**: civic engagement, health outcomes, intergenerational mobility, social capital, reduced incarceration — all well-documented returns to education that never appear in earnings data.
- **Field-of-study effects**: A social work graduate and a finance graduate attend the same university. One fails the EP test; the other passes easily. Is the social work program failing, or is it successfully producing social workers?
- **Student selection and composition**: Institutions serving first-generation students, adult learners, students with disabilities, and students from low-income backgrounds face structural earnings headwinds that have nothing to do with program quality. As [TICAS has noted](https://ticas.org/accountability/ahead-neg-reg-session-2-recap-jan-2026/), students' return on investment is shaped by economic status, race, immigration status, and generational wealth — factors the EP test treats as invisible.
- **Certificate program exemption**: Remarkably, undergraduate certificate programs — which generally have the *lowest* earnings outcomes — are [exempt from the EP test entirely](https://www.naicu.edu/policy-advocacy/advocacy-resources/reconciliation-advocacy-center/frequently-asked-questions-about-the-one-big-beautiful-bill-act/). The PEER Center estimates one in five certificate students is in a program that wouldn't pass.

---

## The Numbers Tell the Story

Our analysis of 6,429 institutions using College Scorecard data reveals the scale of the problem:

| Metric | Value |
|--------|-------|
| Institutions with earnings data | 5,542 |
| Classified as High Risk (fail EP) | 1,264 (22.8%) |
| Within +/-10% of threshold | 699 (12.6%) |
| Within +/-5% of threshold | 377 (6.8%) |
| County earnings variation | 9x (min to max) |
| State threshold variation | 1.4x (min to max) |

The county-level variation in HS earnings is **enormous** — yet the statewide threshold compresses it into a narrow band. The metric operates as if economic geography doesn't exist.

---

## What Would a Better Metric Look Like?

Acknowledging these flaws doesn't mean accountability is wrong. It means the *instrument* needs refinement. A more defensible approach would:

1. **Use local benchmarks**: Compare graduate earnings against county or commuting-zone HS earnings, not statewide aggregates. The data exists — Census ACS B20004 provides county-level HS earnings for 3,200+ counties.

2. **Apply confidence intervals**: Replace the binary pass/fail cliff with a statistical test that accounts for cohort size, earnings variance, and measurement error. Small programs should not be judged on the same terms as programs with thousands of graduates.

3. **Adjust for cost of living**: A dollar earned in rural Alabama is not the same as a dollar earned in San Francisco. Regional price parities from the Bureau of Economic Analysis are readily available.

4. **Include time dynamics**: Measure earnings trajectories, not single snapshots. Programs that show sustained earnings growth over time are fundamentally different from programs with permanently depressed outcomes.

5. **Account for student composition**: Risk-adjust for the demographics and starting conditions of the students served. An institution that takes students from the bottom quartile to the median is providing more value than one that takes students from the top quartile to slightly higher.

6. **Close the certificate loophole**: If earnings accountability is important enough to threaten degree programs, it should apply to certificate programs too — programs where the evidence of poor outcomes is strongest.

---

## Conclusion

The earnings premium test, as enacted in the One Big Beautiful Bill Act, embodies the worst kind of policy design: it takes a reasonable intuition (college should pay off) and operationalizes it with a statistically naive metric. It commits the ecological fallacy. It is vulnerable to Simpson's paradox. It ignores within-state economic geography that varies by a factor of nine. It treats measurement noise as signal. And it exempts the programs with the weakest outcomes.

The institutions most likely to be punished are not the worst actors in higher education — they are the public colleges and community institutions in low-income, rural areas that serve the students with the fewest alternatives. The institutions most likely to be shielded are those in high-cost metros whose graduates clear statewide thresholds by virtue of *location*, not *quality*.

If we are serious about accountability in higher education, we should be serious about the statistics behind it. The earnings premium needs considerable refinement before it is fit for purpose. As it stands, it is a blunt instrument that will do real damage to the institutions and students it claims to protect.

---

*Data and interactive analysis available at the [EP Analyzer](https://ep-analyzer.onrender.com). Source data: College Scorecard, Census ACS B20004, IPEDS. Analysis methodology and code available on [GitHub](https://github.com/malpasocodes/ep-analyzer).*

---

### Sources and Further Reading

- [NASFAA — 2026 Gainful Employment Overview](https://www.nasfaa.org/ge_2026)
- [NASFAA — Deep Dive: Understanding Analyses of New Accountability Frameworks](https://www.nasfaa.org/news-item/38137/Deep_Dive_Understanding_Analyses_of_New_Accountability_Frameworks_Under_the_One_Big_Beautiful_Bill_Act)
- [NAICU — FAQ on the One Big Beautiful Bill Act](https://www.naicu.edu/policy-advocacy/advocacy-resources/reconciliation-advocacy-center/frequently-asked-questions-about-the-one-big-beautiful-bill-act/)
- [Ropes & Gray — Effect of Changes to Title IV in the OBBBA](https://www.ropesgray.com/en/insights/alerts/2025/08/effect-of-changes-to-title-iv-of-the-higher-education-act-in-the-one-big-beautiful-bill)
- [Cooley — Earnings Premium for Nonprofit and Public Universities](https://ed.cooley.com/2025/07/16/big-beautiful-bill-earnings-premium-for-nonprofit-and-public-universities/)
- [Phil Hill / On EdTech — Excellent Research Confirms Flaw in Earnings Premium](https://onedtech.philhillaa.com/p/excellent-research-confirms-flaw-in-earnings-premium)
- [UW-Madison SSTAR — ROI Report on Geographic Variation](https://lrc.sstar.wisc.edu/documents/SSTAR_ROI_report.pdf)
- [AIR — Exploring Geographic Variation in Postsecondary Value](https://www.air.org/project/exploring-geographic-variation-postsecondary-value-among-us-community-colleges)
- [Fordham Institute — What You Make Depends on Where You Live](https://fordhaminstitute.org/national/research/what-you-make-depends-on-where-you-live)
- [SF Fed — Falling College Wage Premiums by Race and Ethnicity](https://www.frbsf.org/research-and-insights/publications/economic-letter/2023/08/falling-college-wage-premiums-by-race-and-ethnicity/)
- [IHEP — New Accountability Framework](https://www.ihep.org/new-accountability-framework-will-help-ensure-higher-education-provides-strong-outcomes-for-all-students/)
- [TICAS — AHEAD Negotiated Rulemaking Recap](https://ticas.org/accountability/ahead-neg-reg-session-2-recap-jan-2026/)
- [Inside Higher Ed — How Talks Over New Earnings Test Could Ensnare Gainful Employment](https://www.insidehighered.com/news/government/student-aid-policy/2025/12/05/how-talks-over-new-earnings-test-could-ensnare)
- [Minneapolis Fed — What Happened to the College Wage Premium?](https://www.minneapolisfed.org/article/2025/what-happened-to-the-college-wage-premium)
- [NBER — Recent Flattening in the Higher Education Wage Premium](https://www.nber.org/system/files/working_papers/w22935/w22935.pdf)
- [Andrew Gelman — Estimating the College Wealth Premium: Not So Easy](https://statmodeling.stat.columbia.edu/2021/03/29/estimating-the-college-wealth-premium-not-so-easy/)
- [Ecological Fallacy — Wikipedia](https://en.wikipedia.org/wiki/Ecological_fallacy)
- [ED.gov — Explanation of Earnings Test and GE Changes](https://www.ed.gov/media/document/2025-ahead-explanation-of-earnings-test-and-ge-changes-112929.pdf)
