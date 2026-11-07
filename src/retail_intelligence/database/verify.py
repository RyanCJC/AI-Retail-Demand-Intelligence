
from sqlalchemy import text

from retail_intelligence.database.connection import engine


CHECKS = {
    "Products": "SELECT COUNT(*) FROM products",
    "Forecasts": "SELECT COUNT(*) FROM demand_forecasts",
    "Inventory policies": "SELECT COUNT(*) FROM inventory_policies",
    "Inventory snapshots": "SELECT COUNT(*) FROM inventory_snapshots",
}


with engine.connect() as connection:

    print("Database record counts:")

    for name, query in CHECKS.items():
        count = connection.execute(text(query)).scalar_one()
        print(f"{name}: {count:,}")

    print("\nIntegrity checks:")

    foreign_keys = connection.execute(
        text("PRAGMA foreign_key_check")
    ).fetchall()

    print("Foreign key violations:", len(foreign_keys))

    invalid_positions = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM inventory_snapshots
            WHERE inventory_position != on_hand + on_order - backorders
        """)
    ).scalar_one()

    print("Invalid inventory positions:", invalid_positions)

    invalid_forecasts = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM demand_forecasts
            WHERE p10 > p50 OR p50 > p90
        """)
    ).scalar_one()

    print("Invalid forecast quantile ordering:", invalid_forecasts)

    missing_products = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM inventory_snapshots AS i
            LEFT JOIN products AS p ON i.product_id = p.id
            WHERE p.id IS NULL
        """)
    ).scalar_one()

    print("Inventory snapshots without products:", missing_products)

    if any([
        foreign_keys,
        invalid_positions,
        invalid_forecasts,
        missing_products,
    ]):
        raise RuntimeError("Database integrity verification failed.")

print("\nDatabase integrity verification passed.")
