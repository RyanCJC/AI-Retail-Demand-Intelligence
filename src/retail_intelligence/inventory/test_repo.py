
from retail_intelligence.database.session import SessionLocal
from retail_intelligence.inventory.repository import InventoryRepository


with SessionLocal() as session:
    repository = InventoryRepository(session)

    context = repository.get_inventory_context(
        product_id="FOODS_1_020_WI_2_evaluation",
        origin_day_num=1829,
        lead_time=7,
        starting_stock_ratio=0.50,
    )

    print(context)
