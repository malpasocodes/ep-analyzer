# AHEAD Session 2 Crosswalk Analysis

## Summary

The AHEAD (Accountability in Higher Education Act Data) Session 2 file from the Department of Education contains 209,321 program-level records across 5,096 institutions. It includes the DOE's own OBBB pass/fail assessment and reveals a **critical difference** in how the EP test benchmark is defined.

## Crosswalk Results

**Join key:** AHEAD `opeid6` → IPEDS `OPEID/100` → `UNITID`, then match on `cipcode` (4-digit CIP) + `credential_level`.

- 99.5% of AHEAD records match to a UNITID (5,024 of 5,096 opeid6 values)
- 171,410 programs matched at the program level (80.2% of ours, 81.9% of theirs)
- 47,102 programs have assessments from both us and AHEAD

## Key Finding: The OBBB Uses Multiple Benchmarks, Not Just State HS Median

**This is the most important discovery.** The AHEAD data reveals that Section 84001 of the OBBB does NOT simply use the same-state HS median earnings as the sole benchmark. The legislation specifies the **lowest** of several benchmarks:

| Benchmark Used | Programs | Share |
|---|---:|---:|
| Same-State HS Median | 97,660 | 46.7% |
| Not Listed in Section 84001 | 41,818 | 20.0% |
| National Same-Field BA Median | 31,320 | 15.0% |
| Same-State BA Median | 15,771 | 7.5% |
| National HS Median | 14,244 | 6.8% |
| National BA Median | 4,710 | 2.3% |
| Same-State, Same-Field BA Median | 3,359 | 1.6% |

For nearly half of programs, the benchmark is NOT the same-state HS median — it's a higher bar (BA-level benchmarks) or a different geographic scope.

**Our EP Analyzer uses a two-tier approach: state HS median for undergraduate programs and state BA median (all fields) for graduate programs (credential levels 4–8).** This aligns with the legislation's broad structure, but differs in the details — we don't use field-specific BA benchmarks, national HS/BA medians, or the certificate exemption.

### Benchmark Rules by Credential Level

The AHEAD data reveals that the legislation assigns benchmarks based on credential level, not uniformly:

**Sub-baccalaureate (certificates, associates):**
- Associates use the **Same-State HS Median** (96.1%) or **National HS Median** (3.9%)
- Undergraduate Certificates are **100% "Not Listed in Section 84001"** — apparently exempt
- Post-Baccalaureate Certificates are also **100% exempt**

**Bachelor's programs:**
- Use the **Same-State HS Median** (81.7%) or **National HS Median** (18.3%)
- Tested against HS-level benchmarks only, same as associates

**Graduate programs (Master's, Doctoral, First Professional, Graduate Certificate):**
- Tested against the **lowest** of several BA-level benchmarks:
  - National Same-Field BA Median (~55%)
  - Same-State BA Median (~29%)
  - National BA Median (~9%)
  - Same-State, Same-Field BA Median (~6%)
- The lowest BA-level benchmark is used — this is the easiest to pass, but still typically higher than HS-level benchmarks

### Benchmark Examples

**1. Same-State HS Median** (46.7% of programs — associates and bachelor's)

> Alabama A&M University, **Biology (Bachelor's)** in AL
> - Earnings: $44,145
> - Benchmark: **$30,927** (AL high school median)
> - Result: **Pass** — earnings exceed the state HS median by 43%
> - All other benchmarks available but not used: BA state field $46,411, BA state $51,030, BA national field $53,672, BA national $60,112

**2. National HS Median** (6.8% — when national HS median > state HS median)

> Oakwood University, **Human Resources Management (Bachelor's)** in AL
> - Earnings: $62,069
> - Benchmark: **$34,808** (national HS median)
> - Result: **Pass** — the national HS median ($34,808) is higher than AL's state HS median ($30,927), so the national figure is the binding test
> - Note: For bachelor's programs, the legislation uses the *higher* of state or national HS median

**3. National Same-Field BA Median** (15.0% — most common for graduate programs)

> Alabama A&M University, **Clinical, Counseling and Applied Psychology (Master's)** in AL
> - Earnings: $48,983
> - Benchmark: **$36,711** (BA state field median for psychology in AL)
> - Result: **Pass** — the lowest BA-level benchmark is the same-state, same-field BA median
> - Available BA benchmarks: state field $36,711, national field $48,653, state $51,030, national $60,112 — the lowest ($36,711) is used

**4. Same-State BA Median** (7.5% — graduate programs where state BA median is lowest)

> Alabama A&M University, **Engineering, Other (Master's)** in AL
> - Earnings: $103,898
> - Benchmark: **$51,030** (AL bachelor's degree median)
> - Result: **Pass** — the state BA median is lower than all field-specific BA benchmarks for this field
> - Available BA benchmarks: state field $82,472, state $51,030, national field $86,596, national $60,112

**5. National BA Median** (2.3% — graduate programs in states with low BA medians)

> Tuskegee University, **Rehabilitation and Therapeutic Professions (Master's)** in AL
> - Earnings: $80,245
> - Benchmark: **$60,112** (national BA median)
> - Result: **Pass** — the national BA median is the binding benchmark because field-specific options are higher
> - Available BA benchmarks: state field $51,545, state $51,030, national field $61,854, national $60,112

**6. Same-State, Same-Field BA Median** (1.6% — when this is the lowest BA option)

> Alabama A&M University, **Biology (Master's)** in AL
> - Earnings: $54,216
> - Benchmark: **$46,411** (BA median for biology graduates in AL)
> - Result: **Pass** — the same-state, same-field BA median ($46,411) is lower than all other BA benchmarks

**7. Not Listed in Section 84001** (20.0% — exempt programs)

> John C. Calhoun State Community College, **Allied Health (Undergraduate Certificate)** in AL
> - Earnings: $55,037
> - Benchmark: **N/A** — program is not subject to the EP test
> - All undergraduate certificates and post-baccalaureate certificates fall in this category

**8. Tie for Lowest Test** (0.2% — two benchmarks are equal)

> Regis University, **Criminology (Master's)** in CO
> - Earnings: $63,202
> - Benchmark: **$63,816** (tied lowest)
> - Result: **Fail** — earnings fall short of the benchmark by $614

### Key Takeaway

The legislation creates a **two-tier system**:
- **Sub-baccalaureate and bachelor's programs** are tested against HS-level earnings (the higher of state or national). This is close to what our EP Analyzer does.
- **Graduate programs** are tested against the lowest of several BA-level benchmarks. These are higher bars, but graduate programs generally clear them. Our EP Analyzer tests these against the HS median instead, which is a lower bar — but one that fewer graduate programs would fail anyway since graduate earnings typically exceed HS benchmarks by wide margins.
- **Certificates** (undergraduate and post-bacc) are exempt entirely — a major carve-out affecting 41,818 programs (20%).

## Pass/Fail Agreement

Of 47,102 programs both sides assessed:
- **Agreement: 82.9%** (39,034 programs)
- Both say fail: 886
- Both say pass: 38,148
- **We say fail, they say pass: 7,613** — we use a lower threshold (state HS median) but flag programs that AHEAD passes because AHEAD uses the minimum of multiple benchmarks
- **They say fail, we say pass: 455** — smaller category

The 7,613 "we fail, they pass" disagreements are dominated by graduate programs where AHEAD uses a BA-level benchmark (4,139 use "National Same-Field BA Median"). These programs fail our state HS median test but pass the DOE's assessment because the legislation assigns graduate programs a different set of benchmarks entirely — the lowest of several BA-level medians. Since graduate earnings typically exceed HS benchmarks by wide margins, the disagreements arise from programs whose earnings fall between the HS median (our threshold) and the BA-level benchmark (the DOE's threshold).

## AHEAD Fail Counts

- `fail_obbb_cip2_wageb = 1`: **1,220** programs fail (of 44,052 assessed) — **2.8% fail rate**
- `mstr_obbb_fail_cip2_wageb = 1`: **2,880** programs fail (of 49,860 assessed) — **5.8% fail rate**
- Our High Risk (reported): **16,999** programs fail — **26.7% of assessed**

**The DOE's assessment is dramatically more favorable than ours.** Only 1,220–2,880 programs fail under their reading of the legislation vs. our 16,999. This gap stems from the multi-benchmark structure: the legislation apparently lets programs pass if they beat ANY of the applicable benchmarks (the lowest one), and for many bachelor's+ programs, BA-level benchmarks set a bar their graduates already clear.

## Implications for EP Analyzer

1. **Our analysis is well-aligned for associates and bachelor's programs** — these use HS-level benchmarks in the legislation, which is what our EP Analyzer does. The legislation uses the higher of state or national HS median; we use only the state median, so we may slightly understate risk in low-threshold states.
2. **Our graduate program thresholds are stricter than the legislation's** — we already use state BA median (all fields) for credential levels 4–8 (since commit f802cc7, avg threshold $68,150). But the legislation picks the *lowest* of four BA benchmarks, including field-specific options that can be substantially lower (e.g., $36,711 for psychology in AL vs. our $51,030 state BA median).
3. **Undergraduate certificates and post-bacc certificates are exempt** — 41,818 programs (20%) are "Not Listed in Section 84001." Our analysis currently includes these. This is the single largest source of overcounting in our risk estimates.
4. **The AHEAD data includes debt-to-earnings (GE) test results** which could add another dimension to our analysis.

## Status

Research-only — no code changes. User will use these findings to inform article writing. Multi-benchmark implementation and GE/debt data integration deferred for later.
