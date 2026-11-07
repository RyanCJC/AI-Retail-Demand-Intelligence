
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(
    r"C:\Users\cjc72\Desktop\SalesForecasting\AI-Retail-Demand-Intelligence"
)

PREDICTION_DIR = (
    PROJECT_ROOT / "data/processed/model_comparison/predictions"
)

OUTPUT_DIR = PROJECT_ROOT / "data/processed/simulated"
OUTPUT_PATH = OUTPUT_DIR / "simulated_inventory_snapshots.parquet"

TARGET_PATH = (
    PREDICTION_DIR / "tft_operational_inventory_targets.parquet"
)

SEED = 42
REVIEW_PERIOD_DAYS = 7
STARTING_STOCK_RATIOS = [0.25, 0.50, 1.00]

rng = np.random.default_rng(SEED)

targets = pd.read_parquet(TARGET_PATH)

records = []

for row in targets.itertuples(index=False):

    protection_period = int(row.protection_period)
    lead_time = protection_period - REVIEW_PERIOD_DAYS

    if lead_time not in [7, 14, 21]:
        raise ValueError(f"Unsupported lead time: {lead_time}")

    order_up_to_level = int(row.order_up_to_level_units)

    for stock_ratio in STARTING_STOCK_RATIOS:

        on_hand = int(np.ceil(order_up_to_level * stock_ratio))

        max_on_order = max(1, int(np.ceil(order_up_to_level * 0.20)))
        max_backorders = max(1, int(np.ceil(order_up_to_level * 0.10)))

        on_order = int(rng.integers(0, max_on_order + 1))
        backorders = int(rng.integers(0, max_backorders + 1))

        inventory_position = (
            on_hand + on_order - backorders
        )

        records.append({
            "origin_day_num": int(row.origin_day_num),
            "id": row.id,
            "demand_class": row.demand_class,
            "lead_time": lead_time,
            "review_period": REVIEW_PERIOD_DAYS,
            "protection_period": protection_period,
            "starting_stock_ratio": stock_ratio,
            "on_hand": on_hand,
            "on_order": on_order,
            "backorders": backorders,
            "inventory_position": inventory_position,
            "order_up_to_level": order_up_to_level,
            "safety_stock": float(row.safety_stock),
            "used_pooled_fallback": bool(row.used_pooled_fallback),
            "simulation_seed": SEED,
        })

inventory = pd.DataFrame(records)

scenario_keys = [
    "origin_day_num",
    "id",
    "lead_time",
    "starting_stock_ratio",
]

if inventory.duplicated(scenario_keys).any():
    raise ValueError("Duplicate inventory scenarios detected.")

if not (
    inventory["inventory_position"]
    == inventory["on_hand"]
    + inventory["on_order"]
    - inventory["backorders"]
).all():
    raise ValueError("Inventory position calculation failed.")

if (inventory["on_hand"] < 0).any():
    raise ValueError("Negative on-hand inventory detected.")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
inventory.to_parquet(OUTPUT_PATH, index=False)

print("Saved:", OUTPUT_PATH)
print("Rows:", len(inventory))
print("Unique SKUs:", inventory["id"].nunique())

print("\nLead-time scenarios:")
print(inventory["lead_time"].value_counts().sort_index())

print("\nStarting-stock scenarios:")
print(inventory["starting_stock_ratio"].value_counts().sort_index())

print("\nInventory position summary:")
print(
    inventory[
        ["on_hand", "on_order", "backorders", "inventory_position"]
    ].describe().round(2)
)

print("\nSample inventory snapshots:")
print(inventory.head(10).to_string(index=False))

print("\nInventory snapshot generation completed.")
