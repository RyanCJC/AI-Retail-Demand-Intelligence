
from pathlib import Path

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from retail_intelligence.database.connection import engine
from retail_intelligence.database import models


PROJECT_ROOT = Path(__file__).resolve().parents[3]

PREDICTION_DIR = (
    PROJECT_ROOT / "data/processed/model_comparison/predictions"
)

SIMULATION_DIR = PROJECT_ROOT / "data/processed/simulated"

FORECAST_PATH = (
    PREDICTION_DIR / "tft_development_predictions_postprocessed.parquet"
)

TARGET_PATH = (
    PREDICTION_DIR / "tft_operational_inventory_targets.parquet"
)

SNAPSHOT_PATH = (
    SIMULATION_DIR / "simulated_inventory_snapshots.parquet"
)

BATCH_SIZE = 5000


def load_source_data():
    forecasts = pd.read_parquet(FORECAST_PATH)
    targets = pd.read_parquet(TARGET_PATH)
    snapshots = pd.read_parquet(SNAPSHOT_PATH)

    required_columns = {
        "forecasts": {
            "id", "origin_day_num", "target_day_num",
            "horizon", "p10", "p50", "p90",
        },
        "targets": {
            "id", "origin_day_num", "demand_class",
            "protection_period", "safety_stock",
            "used_pooled_fallback", "order_up_to_level_units",
        },
        "snapshots": {
            "id", "origin_day_num", "lead_time",
            "review_period", "protection_period",
            "starting_stock_ratio", "on_hand",
            "on_order", "backorders", "inventory_position",
            "simulation_seed",
        },
    }

    for name, dataframe in [
        ("forecasts", forecasts),
        ("targets", targets),
        ("snapshots", snapshots),
    ]:
        missing = required_columns[name] - set(dataframe.columns)

        if missing:
            raise ValueError(
                f"{name} is missing columns: {sorted(missing)}"
            )

    return forecasts, targets, snapshots


def upsert_records(connection, table, records, conflict_columns):
    if not records:
        return

    statement = sqlite_insert(table)

    update_columns = {
        column.name: getattr(statement.excluded, column.name)
        for column in table.columns
        if column.name not in conflict_columns
        and not column.primary_key
    }

    statement = statement.on_conflict_do_update(
        index_elements=conflict_columns,
        set_=update_columns,
    )

    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]
        connection.execute(statement, batch)


def build_records(forecasts, targets, snapshots):
    classification = targets[
        ["id", "demand_class"]
    ].drop_duplicates()

    if classification["id"].duplicated().any():
        raise ValueError(
            "A product has inconsistent demand classifications."
        )

    product_records = classification.rename(
        columns={"id": "id"}
    ).to_dict("records")

    forecast_records = forecasts.rename(
        columns={
            "id": "product_id",
            "p10": "p10",
            "p50": "p50",
            "p90": "p90",
        }
    )[
        [
            "product_id",
            "origin_day_num",
            "target_day_num",
            "horizon",
            "p10",
            "p50",
            "p90",
        ]
    ].to_dict("records")

    policy_data = targets.copy()
    policy_data["lead_time"] = (
        policy_data["protection_period"] - 7
    )
    policy_data["review_period"] = 7
    policy_data["order_up_to_level"] = (
        policy_data["order_up_to_level_units"]
    )

    policy_records = policy_data.rename(
        columns={"id": "product_id"}
    )[
        [
            "product_id",
            "origin_day_num",
            "lead_time",
            "review_period",
            "protection_period",
            "safety_stock",
            "order_up_to_level",
            "used_pooled_fallback",
        ]
    ].to_dict("records")

    snapshot_records = snapshots.rename(
        columns={"id": "product_id"}
    )[
        [
            "product_id",
            "origin_day_num",
            "lead_time",
            "review_period",
            "protection_period",
            "starting_stock_ratio",
            "on_hand",
            "on_order",
            "backorders",
            "inventory_position",
            "simulation_seed",
        ]
    ].to_dict("records")

    return (
        product_records,
        forecast_records,
        policy_records,
        snapshot_records,
    )


def validate_source_keys(forecasts, targets, snapshots):
    checks = [
        (
            forecasts,
            ["id", "origin_day_num", "target_day_num"],
            "forecast",
        ),
        (
            targets,
            ["id", "origin_day_num", "protection_period"],
            "policy",
        ),
        (
            snapshots,
            [
                "id",
                "origin_day_num",
                "lead_time",
                "starting_stock_ratio",
            ],
            "inventory snapshot",
        ),
    ]

    for dataframe, keys, label in checks:
        if dataframe.duplicated(keys).any():
            raise ValueError(
                f"Duplicate {label} keys detected: {keys}"
            )

    if not (
        snapshots["inventory_position"]
        == snapshots["on_hand"]
        + snapshots["on_order"]
        - snapshots["backorders"]
    ).all():
        raise ValueError("Inventory position validation failed.")

    if not (
        targets["order_up_to_level_units"]
        == targets["order_up_to_level_units"].astype(int)
    ).all():
        raise ValueError("Invalid order-up-to level units.")


def main():
    forecasts, targets, snapshots = load_source_data()

    validate_source_keys(forecasts, targets, snapshots)

    (
        products,
        forecast_records,
        policy_records,
        snapshot_records,
    ) = build_records(forecasts, targets, snapshots)

    with engine.begin() as connection:
        upsert_records(
            connection,
            models.Product.__table__,
            products,
            ["id"],
        )

        upsert_records(
            connection,
            models.DemandForecast.__table__,
            forecast_records,
            ["product_id", "origin_day_num", "target_day_num"],
        )

        upsert_records(
            connection,
            models.InventoryPolicy.__table__,
            policy_records,
            ["product_id", "origin_day_num", "protection_period"],
        )

        upsert_records(
            connection,
            models.InventorySnapshot.__table__,
            snapshot_records,
            [
                "product_id",
                "origin_day_num",
                "lead_time",
                "starting_stock_ratio",
            ],
        )

        tables = [
            models.Product,
            models.DemandForecast,
            models.InventoryPolicy,
            models.InventorySnapshot,
        ]

        print("\nDatabase record counts:")

        for model in tables:
            count = connection.execute(
                select(func.count()).select_from(model)
            ).scalar_one()

            print(f"{model.__tablename__}: {count:,}")

    print("\nData ingestion completed successfully.")


if __name__ == "__main__":
    main()
