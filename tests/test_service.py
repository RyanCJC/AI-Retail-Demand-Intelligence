
from retail_intelligence.database.session import SessionLocal
from retail_intelligence.inventory.service import InventoryService


with SessionLocal() as session:
    service = InventoryService(session)

    assessment = service.assess_inventory(
        product_id="FOODS_1_020_WI_2_evaluation",
        origin_day_num=1829,
        lead_time=7,
        starting_stock_ratio=0.50,
    )

    print(assessment)
