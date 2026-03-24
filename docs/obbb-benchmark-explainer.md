# How the OBBB Earnings Test Actually Works: A Plain English Explainer

## The Simple Version Everyone Assumes

Most people read the Earnings Premium test as a single question:

> Do a program's graduates earn more than high school graduates in the same state?

That's how we initially built the EP Analyzer. We've since updated it to use a two-tier approach: state HS median earnings for undergraduate programs and state BA median earnings for graduate programs. But even that doesn't fully capture what the legislation specifies.

**The actual legislation is more complicated.**

## What the Legislation Actually Does

Section 84001 of the One Big Beautiful Bill doesn't apply a single benchmark to every program. It groups programs by credential level and applies different rules to each group.

There are three tiers:

### Tier 1: Not tested at all

**Undergraduate certificates** (38,349 programs) and **post-baccalaureate certificates** (3,469 programs) are not listed in Section 84001. They appear to be **exempt** from the Earnings Premium test entirely. That's 41,818 programs — 20% of all programs in the dataset — that the EP test simply does not apply to.

### Tier 2: Tested against high school earnings

**Associate's degrees** and **bachelor's degrees** are tested against high school graduate earnings. The benchmark is the **higher** of:

- The median earnings of high school graduates **in the same state**
- The median earnings of high school graduates **nationally**

In most states, the state median is lower than the national median ($34,808), so the national figure becomes the binding test. In higher-wage states, the state median is higher and becomes the bar.

This is close to what our EP Analyzer does — we use the same-state HS median. The difference is that the legislation also considers the national HS median and uses whichever is higher, which makes the test slightly harder in low-wage states.

**Example:** A bachelor's program in Alabama. Alabama's HS median is $30,927. The national HS median is $34,808. Under the legislation, the program must beat $34,808 (the higher of the two). Under our EP Analyzer, it only needs to beat $30,927.

### Tier 3: Tested against bachelor's degree earnings

**Graduate programs** — master's, doctoral, first professional degrees, and graduate certificates — face a different test entirely. They are not compared to high school graduates. Instead, they must beat the **lowest** of several bachelor's degree benchmarks:

- Median earnings of bachelor's degree holders **in the same state, same field**
- Median earnings of bachelor's degree holders **in the same state** (all fields)
- Median earnings of bachelor's degree holders **nationally, same field**
- Median earnings of bachelor's degree holders **nationally** (all fields)

The legislation picks whichever of these is lowest — giving the program the easiest possible BA-level bar to clear.

**Example:** A Master's in Clinical Psychology at Alabama A&M.

| Benchmark | Amount |
|---|---:|
| BA holders in psychology, Alabama | $36,711 |
| BA holders (all fields), Alabama | $51,030 |
| BA holders in psychology, nationally | $48,653 |
| BA holders (all fields), nationally | $60,112 |

The lowest is $36,711 (psychology BA holders in Alabama). That's the bar this program must clear. Its graduates earn $48,983, so it passes.

Our EP Analyzer tests graduate programs against the state BA median (all fields) — in Alabama, that's $51,030. This program passes under our tool as well ($48,983 < $51,030 — actually, it would fail our test). The legislation's approach of picking the *lowest* BA benchmark ($36,711) is more lenient than our single state BA median ($51,030).

## Why Does This Matter?

### It changes the fail rate dramatically

Under our EP Analyzer (state HS median for undergrad, state BA median for graduate): **16,999 programs fail** out of 63,582 with reported earnings — a **26.7% fail rate**.

Under the DOE's reading of the legislation: **1,220 programs fail** out of 44,052 assessed — a **2.8% fail rate**.

That's roughly a 14x difference in the number of programs flagged for elimination.

### The certificate exemption is the biggest factor

20% of all programs — mostly short-term vocational certificates — are apparently exempt. These are precisely the programs most likely to fail an HS-earnings test (cosmetology, allied health, dental support). By exempting them, the legislation removes the most vulnerable programs from the test entirely.

### Graduate programs face a higher but more forgiving bar

Graduate programs are tested against BA-level earnings, not HS-level — and our EP Analyzer already does this too (using state BA median since commit f802cc7). But the legislation goes further: it picks the *lowest* of four BA benchmarks (state field, state all, national field, national all), while we use only the state all-fields BA median. The lowest option can be substantially lower — in the psychology example above, $36,711 vs. our $51,030.

### Bachelor's and associate's programs are where the tests most closely align

For these programs, both the legislation and our EP Analyzer use HS-level benchmarks. The main difference is that the legislation uses the higher of state and national HS medians, while we use state-only. This means our tool may slightly understate risk in low-wage states where the national HS median ($34,808) exceeds the state figure.

## Summary Table

| Credential | Benchmark Used | Our EP Analyzer | Programs |
|---|---|---|---:|
| Undergraduate Certificate | **Exempt** | State HS median | 38,349 |
| Associate's | Higher of state or national HS median | State HS median only | 42,933 |
| Bachelor's | Higher of state or national HS median | State HS median only | 68,971 |
| Post-Bacc Certificate | **Exempt** | State BA median | 3,469 |
| Master's | Lowest of 4 BA-level benchmarks | State BA median (all fields) | 33,640 |
| Doctoral | Lowest of 4 BA-level benchmarks | State BA median (all fields) | 11,859 |
| First Professional | Lowest of 4 BA-level benchmarks | State BA median (all fields) | 1,648 |
| Graduate Certificate | Lowest of 4 BA-level benchmarks | State BA median (all fields) | 8,452 |

## What This Means for the EP Analyzer

Our tool already implements the two major tiers: HS-level benchmarks for undergraduate programs and BA-level benchmarks for graduate programs. The remaining gaps are:

1. **Certificate exemption** — we test undergraduate and post-bacc certificates, but the legislation appears to exempt them. This is our largest source of overcounting.
2. **National HS floor** — for associates and bachelor's, the legislation uses the higher of state and national HS medians. We use state-only, which may slightly understate risk in low-wage states.
3. **Lowest-of-four BA logic** — for graduate programs, we use the state all-fields BA median, but the legislation picks the lowest of four BA benchmarks (including field-specific options). This makes our graduate test stricter than the legislation's in many cases.

These distinctions matter for anyone trying to predict which specific programs would actually lose federal aid under the OBBB. Our tool remains a valid stress test — it just applies a somewhat different (and in some cases stricter) bar than the legislation technically specifies.
