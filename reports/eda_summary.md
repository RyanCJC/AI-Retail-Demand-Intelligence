# Exploratory Data Analysis Summary

**Project:** AI-Retail-Demand-Intelligence  
**Dataset:** M5 Walmart Sales Forecasting Accuracy  
**Source:** Zenodo, DOI 10.5281/zenodo.12636070, CC BY 4.0  
**Download date:** 2026-11-01  
**Notebooks analysed:** `notebooks/01_Data-Import-&-Audit.ipynb`, `notebooks/02_EDA.ipynb`  
**Report generated from:** executed notebook cells and direct inspection of `data/raw/` and `data/metadata/`

---

## 1. Executive Summary

The M5 Forecasting Accuracy dataset provides daily unit-sales history for 30,490 product-store series across three US states (California, Texas, Wisconsin) over 1,941 calendar days (2011-01-29 to 2016-06-19), supplemented by a price table and a calendar with event and SNAP indicators.

Key findings from the EDA:

- Demand is highly intermittent: **68.0% of all series-day observations are zero sales**.
- Demand-pattern classification (Syntetos–Boylan) shows **72.65% of series are intermittent**, 18.25% lumpy, 6.26% smooth, and 2.85% erratic; no series are entirely without demand.
- Sales peak on weekends (Saturday highest) and are strongest in late summer; November and December are the weakest months on average.
- Average daily sales are higher on SNAP days than non-SNAP days in all three states (CA, TX, WI), a descriptive association only — no causal claim is made.
- Event days show a slightly lower mean daily sales but substantially higher variability than non-event days.
- Data quality is good: no missing or duplicate rows in `sales` or `sell_prices`; missing values in `calendar` are confined to event fields, which is expected for days without recorded events.

These findings motivate forecasting features that capture intermittency (zero-inflation), weekly and monthly seasonality, price, SNAP, and event calendars, and suggest modelling approaches that can handle highly skewed, zero-heavy demand.

---

## 2. Dataset Overview

The raw data consists of three files retained in `data/raw/` (excluded from Git version control per `data/README.md`).

| File | Rows | Columns | Description |
|---|---:|---:|---|
| `sales_train_evaluation.csv` | 30,490 | 1,947 | Daily unit sales per product-store series |
| `calendar.csv` | 1,969 | 14 | Date, weekday, month, year, event, and SNAP indicators |
| `sell_prices.csv` | 6,841,121 | 4 | Unit price per item-store-week |

### Series and dimension counts

| Dimension | Unique values |
|---|---:|
| Product-store series (`id`) | 30,490 |
| Items (`item_id`) | 3,049 |
| Departments (`dept_id`) | 7 |
| Categories (`cat_id`) | 3 (FOODS, HOBBIES, HOUSEHOLD) |
| Stores (`store_id`) | 10 |
| States (`state_id`) | 3 (CA, TX, WI) |

### Time coverage

- **Sales columns:** `d_1` through `d_1,941` (1,941 daily observations per series).
- **Calendar date range:** 2011-01-29 to 2016-06-19 (1,969 unique dates).
- **Total series-day observations:** 59,181,090.

### Relevant characteristics

- `sales_train_evaluation.csv` is the evaluation-set history used as the primary sales source.
- Each row is one item-store series; the 1,941 `d_*` columns hold daily unit sales.
- Prices are at item-store-week granularity (`sell_prices.csv`), requiring join via `wm_yr_wk` to align with daily sales.
- Calendar SNAP indicators (`snap_CA`, `snap_TX`, `snap_WI`) and event flags are state/day specific.

---

## 3. Overall Sales Trends

### Daily sales trend

Total daily sales across all series were aggregated by summing the `d_*` columns for each day and joined to the calendar date. A line plot of total daily units sold over time is rendered in `notebooks/02_EDA.ipynb` ("Total Daily Retail Sales Across All Series"). The series exhibits visible variation across the 5+ year horizon rather than a flat baseline.

### Monthly seasonality

Average daily total sales by calendar month (all states combined):

| Month | Avg daily units |
|---:|---:|
| January | 33,832 |
| February | 34,645 |
| March | 34,339 |
| April | 34,432 |
| May | 34,085 |
| June | 35,001 |
| July | 35,122 |
| August | 35,947 |
| September | 35,479 |
| October | 34,713 |
| November | 33,291 |
| December | 32,980 |

August is the strongest month on average (~35,947 units/day); December is the weakest (~32,980 units/day). The spread between peak and trough months is modest relative to overall volume, indicating seasonality is present but not dominant at the aggregate level.

### Weekly seasonality

Average daily total sales by weekday:

| Weekday | Avg daily units |
|---:|---:|
| Saturday | 41,706 |
| Sunday | 41,304 |
| Monday | 32,995 |
| Tuesday | 30,500 |
| Wednesday | 30,130 |
| Thursday | 30,321 |
| Friday | 34,357 |

Weekend sales (Saturday/Sunday) are clearly higher than weekdays, with Wednesday the lowest. This weekly pattern is rendered as a bar chart ("Average Daily Sales by Weekday") in `notebooks/02_EDA.ipynb`.

### Notable observations

- Sales fluctuate day-to-day with no single smooth trend line; weekly and monthly cycles are the most visible structure at aggregate level.
- All figures referenced in this section are produced inline in `notebooks/02_EDA.ipynb`; no image files were exported to `reports/`.

---

## 4. Sales by Category

Total sales were aggregated by `cat_id` across all days. A line plot comparing daily sales trajectories for FOODS, HOBBIES, and HOUSEHOLD is rendered in `notebooks/02_EDA.ipynb` ("Daily Sales by Product Category").

### Zero-sales share by category

| Category | Total obs | Zero obs | Zero-sales share |
|---:|---:|---:|---:|
| HOBBIES | 10,966,650 | 8,460,679 | 77.15% |
| HOUSEHOLD | 20,322,270 | 14,551,192 | 71.60% |
| FOODS | 27,892,170 | 17,229,948 | 61.77% |

**Interpretation:** FOODS has both the largest absolute volume and the lowest zero-sales share (demand is most frequent). HOBBIES has the highest zero-sales share (most intermittent demand). These are descriptive comparisons; no causal explanation is implied by category membership.

### Categories with higher/lower sales

FOODS accounts for the largest share of total unit volume, consistent with it having the most non-zero observations. HOBBIES shows the sparsest demand. No numeric category-total table was produced in the notebooks beyond the zero-share comparison above; category rankings are inferred from the zero-sales analysis and the plotted daily trajectories.

---

## 5. Sales by Store and State

### Sales by state

Total daily sales by `state_id` are plotted in `notebooks/02_EDA.ipynb` ("Daily Sales by State"), with one line per state over day numbers 1–1,941.

### Sales by store

Store-level daily sales are plotted per state in `notebooks/02_EDA.ipynb` ("Daily Sales by Store — {state}"), with one line per store within each state. These visualisations allow comparison of store trajectories within CA, TX, and WI.

**Limitation:** No aggregate numerical store-ranking table (e.g., total units per store) was produced in the notebooks; store-level conclusions are limited to what can be read from the plotted lines. A store-level numeric summary has not yet been evaluated.

---

## 6. Calendar and Event Analysis

### Weekday and weekend patterns

As shown in Section 3, weekend days (Saturday, Sunday) record the highest average daily sales; mid-week days (Tuesday–Thursday) are lowest. This is a descriptive pattern across all states combined.

### Event and holiday patterns

A binary `has_event` flag was created from `event_name_1` / `event_name_2` non-nullity. Average total daily sales on event vs. non-event days:

| Event day | Mean daily units | Median | Std dev | Days |
|---:|---:|---:|---:|---:|
| No | 34,609 | 33,817 | 7,202 | 1,783 |
| Yes | 33,030 | 33,957 | 9,503 | 158 |

**Observations (descriptive only):**
- Mean daily sales are slightly lower on event days (33,030 vs 34,609), but event days show markedly higher variability (std 9,503 vs 7,202).
- Median sales are marginally higher on event days (33,957 vs 33,817).

**Caution:** This is an unadjusted descriptive comparison. Event days are a small fraction of the calendar (158 of 1,941 sales days), and differences may be driven by confounding factors (seasonality, state mix, price changes). No causal claim that events increase or decrease sales is supported by this analysis.

### Calendar data quality

- `calendar.csv` has 7,542 missing values, all concentrated in event fields (`event_name_1`, `event_type_1`, `event_name_2`, `event_type_2`), which is expected for days without recorded events. Date, weekday, month, year, `wm_yr_wk`, and all SNAP columns have zero missing values.
- No duplicate rows in `calendar`.

---

## 7. SNAP Analysis

### What the SNAP indicators represent

SNAP (Supplemental Nutrition Assistance Program) is a US government food-assistance programme. In M5, `calendar.csv` contains three binary indicators — `snap_CA`, `snap_TX`, `snap_WI` — where `1` marks a SNAP benefit-availability day and `0` a non-SNAP day, for California, Texas, and Wisconsin respectively. These are intended as calendar features for demand forecasting and to examine sales-pattern differences around benefit-availability days.

### Average daily sales by SNAP status and state

For each state, daily sales for that state were averaged over SNAP vs. non-SNAP days:

| State | Non-SNAP avg daily sales | SNAP avg daily sales | SNAP days | Non-SNAP days |
|---:|---:|---:|---:|---:|
| CA | 14,658 | 15,823 | 650 | 1,319 |
| TX | 9,544 | 10,644 | 650 | 1,319 |
| WI | 8,893 | 10,833 | 650 | 1,319 |

**Observation:** Average daily sales are higher on SNAP days than non-SNAP days in all three states. The uplift is proportionally largest in WI (~21.8%) and smallest in CA (~8.0%). A grouped bar chart ("Average Daily Sales by SNAP Status and State") is rendered in `notebooks/02_EDA.ipynb`.

**Caveat:** This is an unadjusted descriptive comparison across all products in a state. SNAP days are not randomly assigned and may coincide with other calendar effects. No causal claim that SNAP benefits cause higher sales is made; the result only documents an association in the observed data.

### Category-level SNAP analysis

Not performed. SNAP differences across product categories were not computed in the notebooks; this has not yet been evaluated.

---

## 8. Demand Pattern Classification

### Methodology (Syntetos–Boylan)

Each of the 30,490 product-store series was classified using two measures computed over the active period (first non-zero sale day through the last non-zero sale day):

- **ADI (Average Demand Interval):** `active_period / number_of_nonzero_days` — average number of periods between non-zero demand occurrences.
- **CV² (Squared Coefficient of Variation):** `var(nonzero_demand) / mean(nonzero_demand)^2` — variability of non-zero demand sizes.

Classification thresholds (Syntetos–Boylan):

| Demand pattern | ADI | CV² | Description |
|---|---:|---:|---|
| Smooth | < 1.32 | < 0.49 | Frequent, relatively stable demand |
| Erratic | < 1.32 | ≥ 0.49 | Frequent, highly variable demand |
| Intermittent | ≥ 1.32 | < 0.49 | Infrequent, stable demand sizes |
| Lumpy | ≥ 1.32 | ≥ 0.49 | Infrequent, highly variable demand |

Series with no demand at all would be classed `no_demand`; none occurred in this dataset.

### Distribution of demand classes

| Demand class | Series | % of series | Mean ADI | Mean CV² | Zero-sales share (active days) |
|---|---:|---:|---:|---:|---:|
| Intermittent | 22,150 | 72.65% | 4.89 | 0.283 | 67.11% |
| Lumpy | 5,564 | 18.25% | 2.89 | 0.772 | 53.43% |
| Smooth | 1,908 | 6.26% | 1.17 | 0.368 | 13.97% |
| Erratic | 868 | 2.85% | 1.21 | 0.695 | 16.74% |
| **Total** | **30,490** | **100.00%** | — | — | — |
| No demand | 0 | 0.00% | — | — | — |

A bar chart of this distribution ("Distribution of Demand Patterns") is rendered in `notebooks/01_Data-Import-&-Audit.ipynb`; the zero-share-by-class table is in `notebooks/02_EDA.ipynb`.

### Active-period context

- Mean active period: ~1,535 days (median ~1,782; min 96; max 1,941).
- Mean non-zero days per series: ~621 (median ~518; min 12; max 1,938).

### Implications for forecasting

- **Intermittent demand dominates** (~73% of series), meaning most series have long stretches of zero sales. Point-forecast accuracy metrics (e.g., RMSSE) can be misleadingly dominated by correctly forecasting zeros.
- **Lumpy series** (~18%) combine infrequent demand with variable quantities — difficult for both intermittent and volume models.
- Smooth series are a small minority (~6%); models optimised for smooth demand will perform poorly on the majority of series.
- Modelling should therefore account for: (a) a zero-inflation / occurrence component, (b) a demand-size component conditional on non-zero, and (c) demand-class-stratified evaluation rather than a single aggregate metric.

---

## 9. Data Quality Findings

| Dataset | Missing values | Duplicate rows | Notes |
|---|---:|---:|---|
| `sales_train_evaluation.csv` | 0 | 0 | Complete; 30,490 series × 1,941 days |
| `calendar.csv` | 7,542 | 0 | All missing values in event fields (`event_name_1/2`, `event_type_1/2`); expected for days without events. Date, SNAP, and time fields complete. |
| `sell_prices.csv` | 0 | 0 | Complete; 6,841,121 item-store-week price records |

### Zero-sales observations

- Total series-day observations: 59,181,090
- Zero-sales observations: 40,241,819
- **Zero-sales share: 68.0%**

Zero-sales share by demand class (active days only): intermittent 67.11%, lumpy 53.43%, erratic 16.74%, smooth 13.97%. By category: HOBBIES 77.15%, HOUSEHOLD 71.60%, FOODS 61.77%.

### Missing prices

`sell_prices.csv` contains no missing `sell_price`, `item_id`, `store_id`, or `wm_yr_wk`. However, price data is at weekly granularity, so daily sales days within a week share one price; price coverage per series-day depends on the join to `wm_yr_wk`. The alignment of first price week to first sale day was inspected in `notebooks/02_EDA.ipynb` ("Compare First Sales and First Price"), but no aggregate summary of price-availability gaps was produced — this has not yet been evaluated.

### Limitations

- M5 is the evaluation partition of the Walmart dataset; findings may not generalise to the full training partition or other retail contexts.
- All calendar/event/SNAP comparisons are unadjusted and descriptive; confounding is not controlled.
- No saved image exports exist; charts are inline notebook outputs only.
- Store-level numerical summaries and category-level SNAP analysis were not produced.

---

## 10. Implications for Forecasting

### Findings that influence feature engineering

1. **Intermittency (68.0% zeros):** Features should encode time-since-last-sale, count of recent non-zero days, and zero-run length. A two-part model (occurrence + size) is strongly indicated.
2. **Weekly seasonality:** Encode `weekday`, `is_weekend`, and lagged sales at multiples of 7 days.
3. **Monthly seasonality:** Encode `month` and seasonal lags (e.g., same month prior year).
4. **Calendar events:** Encode `has_event`, event name/type, days-to/since-nearest-event.
5. **SNAP:** Encode `snap_<state>` flags and days-to/since-SNAP-day for CA, TX, WI.
6. **Price:** Encode current `sell_price`, price changes, and lagged price; align weekly price to daily sales via `wm_yr_wk`.
7. **Historical sales:** Rolling means, rolling sums, exp-weighted averages, and lags at 1, 7, 28, and 365 days are natural candidates given the identified cycles.

### Relevant feature groups

| Feature group | Candidate features | Rationale |
|---|---|---|
| Calendar | `weekday`, `month`, `is_weekend`, `has_event`, `event_name`, `snap_CA/TX/WI` | Captures weekly/monthly seasonality and event/SNAP effects observed in Sections 3, 6, 7 |
| Price | `sell_price`, price lag, price change | Price table is available; first-price-week alignment was inspected |
| Historical sales | Lags (1, 7, 28, 365), rolling mean/sum, EWMA, zero-run length | Series show strong autocyclic structure and high intermittency |
| Demand class | `demand_class` (smooth/erratic/intermittent/lumpy) | Enables class-aware modelling per Section 8 |

### Why demand intermittency and seasonality matter

With 68.0% zero observations and ~73% of series classified intermittent, a model that only predicts mean demand will systematically over-forecast most series. Separating "whether demand occurs" from "how much" is essential. Weekly and monthly seasonality provide predictable structure that calendar and lag features can exploit.

### Modelling challenges (LightGBM, CatBoost, TFT)

No model training or evaluation has been performed, so no performance claims are made. Anticipated challenges:

- **LightGBM / CatBoost (gradient-boosted trees):** Handle tabular feature matrices well and can learn interactions between price, SNAP, and calendar flags, but require explicit construction of lag/rolling features and are not sequence-native; long-range dependencies (e.g., yearly seasonality) must be hand-engineered. They do not natively model the zero-inflated distribution, so a two-part or quantile approach may be needed.
- **Temporal Fusion Transformer (TFT):** Sequence-native and designed for multi-horizon forecasting with static covariates (item/store/state/category) and time-varying covariates (price, SNAP, events, lags). Well suited to intermittency via attention over history, but more complex to tune, requires careful handling of the high zero fraction, and longer training/inference than tree models.
- **Common challenge across all three:** evaluation metric choice. With 68% zeros and intermittent/lumpy dominance, RMSSE/MAE can be dominated by zero forecasts; quantile or class-stratified metrics are advisable.

---

## Appendix: Data provenance

- Raw files retained in `data/raw/`; excluded from Git.
- Derived metadata `data/metadata/series_classes.parquet` produced by `notebooks/01_Data-Import-&-Audit.ipynb` (30,490 series × 13 columns including `adi`, `cv2`, `demand_class`).
- All statistics in this report were computed from the executed notebooks and direct reads of `data/raw/*.csv` and `data/metadata/series_classes.parquet` on 2026-11-02. No statistics were invented or assumed.
