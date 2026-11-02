# Data Dictionary

**Project:** AI-Retail-Demand-Intelligence  
**Dataset:** M5 Walmart Sales Forecasting Accuracy  
**Source:** Zenodo, DOI 10.5281/zenodo.12636070  
**Licence:** CC BY 4.0 (verified from `data/README.md`, which cites the Zenodo record)  
**Download date:** 2026-11-01  
**Primary sales file used:** `sales_train_evaluation.csv` (not `sales_train_validation.csv`)

---

## 1. Dataset Information

### Name and source
The M5 Forecasting Accuracy dataset, hosted on Zenodo (DOI 10.5281/zenodo.12636070) under CC BY 4.0.

### Description and purpose
The dataset contains daily unit-sales records for product-store combinations, together with a calendar and a selling-price table. It is designed for retail demand forecasting, with the goal of predicting future unit sales for each item-store series. In this project, `sales_train_evaluation.csv` is used as the primary sales history; the evaluation partition is the source of truth for the historical period covered.

### Scope and historical coverage
- **Product-store series:** 30,490 unique series (`id`)
- **Items:** 3,049 unique items across 7 departments and 3 categories
- **Stores:** 10 unique stores across 3 states (CA, TX, WI)
- **Daily sales columns:** `d_1` through `d_1,941` (1,941 daily observations per series)
- **Calendar date range:** 2011-01-29 to 2016-06-19 (1,969 unique dates)
- **Sales observations span:** `d_1` to `d_1,941`, mapped to the first 1,941 calendar dates

---

## 2. Source Files

Three original CSV files are retained in `data/raw/` (excluded from Git version control per `data/README.md`):

| File | Rows | Columns | Purpose |
|---|---:|---:|---|
| `sales_train_evaluation.csv` | 30,490 | 1,947 | Primary sales history: one row per product-store series, with metadata columns and 1,941 daily sales columns |
| `calendar.csv` | 1,969 | 14 | Date, time, event, and SNAP attributes for each day |
| `sell_prices.csv` | 6,841,121 | 4 | Selling price per item-store-retail-week |

---

## 3. Sales Dataset (`sales_train_evaluation.csv`)

### Structure

| Column | Data type | Description |
|---|---|---|
| `id` | object | Unique product-store series identifier, e.g. `HOBBIES_1_001_CA_1_evaluation`. Composite of item, store, state, and partition |
| `item_id` | object | Product identifier |
| `dept_id` | object | Department identifier |
| `cat_id` | object | Product category identifier (FOODS, HOBBIES, HOUSEHOLD) |
| `store_id` | object | Store identifier |
| `state_id` | object | State identifier (CA, TX, WI) |
| `d_1` … `d_1,941` | int64 | Daily unit sales for day 1 through day 1,941 |

### Metadata columns
- `id`: fully qualified series key. Example value observed: `HOBBIES_1_001_CA_1_evaluation`.
- `item_id`: product-level key used to join with `sell_prices.csv`.
- `dept_id`: department grouping above category.
- `cat_id`: product category (FOODS, HOBBIES, HOUSEHOLD).
- `store_id`: store-level key used to join with `sell_prices.csv`.
- `state_id`: US state (CA, TX, WI) used for state-level SNAP indicators and geographic analysis.

### Daily sales columns
The 1,941 columns `d_1` through `d_1,941` record integer unit sales for each consecutive day. Column `d_n` corresponds to the `n`-th day in the sales history and maps to calendar rows via the `d` column in `calendar.csv`. All values are non-negative integers representing units sold; a value of `0` indicates no units sold on that day. These columns are grouped into a single documented range rather than listed individually.

### Notes
- No missing values and no duplicate rows were found.
- The `_evaluation` suffix in `id` identifies this file as the evaluation partition.

---

## 4. Calendar Dataset (`calendar.csv`)

### Columns

| Column | Data type | Nulls | Description |
|---|---|---:|---|
| `date` | datetime64 | 0 | Calendar date (2011-01-29 to 2016-06-19) |
| `wm_yr_wk` | int64 | 0 | Retail week identifier used to join with `sell_prices.csv` |
| `weekday` | object | 0 | Day-of-week name (e.g. Saturday) |
| `wday` | int64 | 0 | Day-of-week number (1 = Saturday …) |
| `month` | int64 | 0 | Month number (1–12) |
| `year` | int64 | 0 | Year |
| `d` | object | 0 | Sales-day identifier (`d_1` … `d_1,969`); joins sales columns to calendar dates |
| `event_name_1` | object | 1,807 | Primary event name, null when no primary event |
| `event_type_1` | object | 1,807 | Primary event type, null when no primary event |
| `event_name_2` | object | 1,964 | Secondary event name, null when no secondary event |
| `event_type_2` | object | 1,964 | Secondary event type, null when no secondary event |
| `snap_CA` | int64 | 0 | SNAP indicator for California (1 = benefit day, 0 = non-benefit day) |
| `snap_TX` | int64 | 0 | SNAP indicator for Texas (1 = benefit day, 0 = non-benefit day) |
| `snap_WI` | int64 | 0 | SNAP indicator for Wisconsin (1 = benefit day, 0 = non-benefit day) |

### SNAP indicators
SNAP (Supplemental Nutrition Assistance Program) is a US government food-assistance programme. Each `snap_<state>` column is binary: `1` marks a day when benefits are available in that state, `0` otherwise. All three SNAP columns have zero missing values; every calendar day has a recorded SNAP status per state.

### Missing-value patterns
Missing values in `calendar.csv` are confined to the event columns (`event_name_1`, `event_type_1`, `event_name_2`, `event_type_2`), which is expected for days without recorded events. Date, `wm_yr_wk`, `weekday`, `wday`, `month`, `year`, `d`, and all SNAP columns are complete. No duplicate rows were found.

---

## 5. Sell Prices Dataset (`sell_prices.csv`)

### Columns

| Column | Data type | Nulls | Description |
|---|---|---:|---|
| `store_id` | object | 0 | Store identifier |
| `item_id` | object | 0 | Product identifier |
| `wm_yr_wk` | int64 | 0 | Retail week identifier |
| `sell_price` | float64 | 0 | Unit selling price |

### Price association
Each row records the unit selling price (`sell_price`) for a specific item (`item_id`) in a specific store (`store_id`) during a specific retail week (`wm_yr_wk`). Prices are at item-store-week granularity; multiple rows may share the same `wm_yr_wk` for different item-store pairs, and the same item-store pair appears across multiple weeks when its price changes. No missing values or duplicate rows were found.

---

## 6. Dataset Relationships

### Keys and joins

| Relationship | Left key | Right key | Join type |
|---|---|---|---|
| Sales metadata ↔ prices | `item_id`, `store_id` | `item_id`, `store_id` | Many-to-many (via weekly price rows) |
| Daily sales ↔ calendar | `d_n` column suffix → `d` | `d` | One-to-one per day |
| Weekly prices ↔ calendar | `wm_yr_wk` | `wm_yr_wk` | Many-to-one (many weeks per date range) |

### Primary / composite keys
- **Sales:** `id` is the unique series key; `(item_id, store_id)` identifies a product-store pair.
- **Calendar:** `d` is the unique day key; `date` and `wm_yr_wk` are also unique per day.
- **Sell prices:** no single unique column; `(store_id, item_id, wm_yr_wk)` forms the natural composite key for a price observation.

### Join notes
- Sales metadata joins to prices on `item_id` and `store_id`; because prices are weekly, one series maps to many price rows over time.
- Daily sales columns map one-to-one to calendar days via `d` (e.g. `d_1` → the calendar row where `d == 'd_1'`).
- Weekly prices map to calendar dates via `wm_yr_wk`; a date's week can be looked up from `calendar.wm_yr_wk`.

---

## 7. Derived Variables and Analytical Features

The following variables were created in the notebooks and persisted to `data/metadata/series_classes.parquet` or computed inline in `notebooks/02_EDA.ipynb`.

### `series_classes.parquet` (from `notebooks/01_Data-Import-&-Audit.ipynb`)

| Variable | Source | Calculation | Interpretation |
|---|---|---|---|
| `id` | sales | copied from `sales.id` | Series identifier |
| `item_id` | sales | copied | Product identifier |
| `dept_id` | sales | copied | Department |
| `cat_id` | sales | copied | Product category |
| `store_id` | sales | copied | Store identifier |
| `state_id` | sales | copied | State identifier |
| `first_demand_day` | sales matrix | 1-indexed position of first non-zero sale: `int(nonzero_positions[0] + 1)`; `NaN` if no demand | First day the series recorded a sale |
| `active_period` | sales matrix | `number_of_days - nonzero_positions[0]`; `0` if no demand | Days from first sale through the final observed day |
| `nonzero_days` | sales matrix | Count of days with sales > 0 | Number of active sales days |
| `zero_days_active` | sales matrix | `active_period - nonzero_days` | Number of zero-sales days within the active period |
| `adi` | sales matrix | `active_period / len(nonzero_demand)`; `NaN` if no demand | Average Demand Interval: mean days between non-zero demand |
| `cv2` | sales matrix | `var(nonzero_demand, ddof=0) / mean(nonzero_demand)^2`; `NaN` if no demand or mean == 0 | Squared Coefficient of Variation of non-zero demand sizes |
| `demand_class` | `adi`, `cv2` | Thresholds: ADI < 1.32 & CV² < 0.49 → smooth; ADI < 1.32 & CV² ≥ 0.49 → erratic; ADI ≥ 1.32 & CV² < 0.49 → intermittent; ADI ≥ 1.32 & CV² ≥ 0.49 → lumpy; NaN → no_demand | Syntetos–Boylan demand pattern class |

### Demand class distribution (computed result)

| Demand class | Series | % of series |
|---|---:|---:|
| Intermittent | 22,155 | 72.66% |
| Lumpy | 5,572 | 18.27% |
| Smooth | 1,903 | 6.24% |
| Erratic | 860 | 2.82% |
| No demand | 0 | 0.00% |

### Inline derived features (`notebooks/02_EDA.ipynb`)

| Variable | Calculation | Interpretation |
|---|---|---|
| `daily_sales.total_sales` | Sum of all `d_*` columns per day | Total units sold across all series each day |
| `daily_sales.day_num` | Integer parsed from `d` column name | Sequential day number |
| `daily_sales.date` | Merged from `calendar` on `d` | Calendar date for each sales day |
| `daily_sales.weekday / month / year` | Merged from `calendar` | Time attributes for seasonality analysis |
| `state_day_sales` | `sales.groupby("state_id")[d_cols].sum().T` merged with calendar | Per-state daily sales joined to SNAP/event flags |
| `comparison.snap_status` | `snap_<state>` mapped `{0: "Non-SNAP", 1: "SNAP"}` | Day classified as SNAP or non-SNAP for a state |
| `calendar.has_event` | `event_name_1.notna() \| event_name_2.notna()` | Binary flag: day has at least one recorded event |
| `first_price_week.wm_yr_wk` | `sell_prices.groupby(["item_id","store_id"])["wm_yr_wk"].min()` | First week a price exists for each item-store pair |
| `first_price_week.first_calendar_date` | `calendar.groupby("wm_yr_wk")["date"].min()` merged on `wm_yr_wk` | First calendar date of the first price week |
| `first_availability.first_sale_date` | Calendar date for `first_demand_day` | Date of first observed sale |
| `first_availability.days_between_price_and_sale` | `first_sale_date - first_calendar_date` | Days between first available price and first observed sale |

---

## 8. Data Processing and Assumptions

### Missing values
- `sales_train_evaluation.csv`: no missing values.
- `sell_prices.csv`: no missing values.
- `calendar.csv`: missing values only in event columns (`event_name_1`, `event_type_1`, `event_name_2`, `event_type_2`), interpreted as days with no recorded event. Warnings are suppressed in the notebook (`warnings.filterwarnings("ignore")`), but no imputation is performed.

### Zero-sales observations
- A daily sales value of `0` means no units were sold that day for that series.
- Overall zero-sales share: 68.0% of all series-day observations (40,241,819 / 59,181,090).
- Zero-sales share is computed both overall and by demand class / category. Within a series' active period (after first sale), zeros are counted as `zero_days_active`.
- Days before `first_demand_day` (pre-first-sale) are treated as outside the active period and are not included in `zero_days_active` or ADI/CV² calculations.

### Pre-first-sale vs. subsequent zeros
- `first_demand_day` marks the first day with a non-zero sale. All earlier days have sales of 0 but are excluded from the active period.
- `active_period` starts at `first_demand_day` and runs to the final day (`d_1,941`).
- `zero_days_active` counts zeros only within the active period, so pre-launch zeros do not inflate the intermittency measures.

### Exclusions and transformations
- No rows were dropped from the source sales file; all 30,490 series are retained.
- No series were excluded for having no demand (zero such series exist).
- `series_classes` is saved to Parquet for efficient reuse; the original CSV files are unchanged.
- Calendar `date` is converted to datetime in the notebooks.

### Assumptions about missing prices
`sell_prices.csv` contains no missing `sell_price`, `item_id`, `store_id`, or `wm_yr_wk`. The notebook inspects alignment between the first price week and first sale date (`days_between_price_and_sale`) but does not aggregate price-availability gaps. No assumption is made that every series-day has a matching price; prices are weekly and must be joined via `wm_yr_wk`, and the coverage of price data relative to every sales day has not been quantified.

---

## 9. Data Limitations

- **Observed sales vs. unconstrained demand:** Recorded sales are censored by stock availability. A zero sales day may reflect no customer demand or an out-of-stock condition; the data cannot distinguish between the two.
- **First observed sale ≠ launch date:** `first_demand_day` is the first day with a recorded non-zero sale in this history window. A product may have been sold earlier (outside this window) or may have had zero sales immediately after launch. It should not be interpreted as the true product introduction date.
- **Evaluation partition only:** `sales_train_evaluation.csv` is the evaluation partition of the M5 dataset; findings may not generalise to the full training partition or to other retail contexts.
- **Unadjusted comparisons:** Calendar, event, and SNAP comparisons in the EDA are descriptive and unadjusted; confounding factors (seasonality, state mix, price changes) are not controlled for, so no causal claims are supported.
- **SNAP state coverage:** SNAP indicators exist only for CA, TX, and WI; all series in this dataset are in those states, but the indicators do not cover other regions.
- **Price granularity:** Prices are weekly (`wm_yr_wk`), while sales are daily. Alignment of weekly price to daily sales is not guaranteed to reflect intra-week price changes.
- **No saved chart exports:** Visualisations are inline notebook outputs; no image files were exported to `reports/`.
