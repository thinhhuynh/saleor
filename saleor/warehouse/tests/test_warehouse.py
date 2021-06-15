import pytest

from saleor.warehouse import WarehouseClickAndCollectOption

from ...shipping.models import ShippingZone
from ..models import Warehouse


def test_get_first_warehouse_for_channel_no_shipping_zone(
    warehouses_with_different_shipping_zone, channel_USD
):
    for shipping_zone in ShippingZone.objects.all():
        shipping_zone.channels.all().delete()
    # At this point warehouse has no shipping zones; getting the first warehouse for
    # channel should return None.
    warehouse = Warehouse.objects.get_first_warehouse_for_channel(channel_USD.pk)
    assert warehouse is None


def test_get_first_warehouse_for_channel(warehouses, channel_USD):
    warehouse_usa = warehouses[1]
    shipping_zone = ShippingZone.objects.create(name="USA", countries=["US"])
    shipping_zone.channels.add(channel_USD)
    warehouse_usa.shipping_zones.add(shipping_zone)

    first_warehouse = Warehouse.objects.get_first_warehouse_for_channel(channel_USD.pk)
    assert first_warehouse == warehouse_usa
import pytest

from saleor.warehouse import WarehouseClickAndCollectOption

from ..models import Warehouse


def test_applicable_for_click_and_collect_finds_warehouse_with_all_and_local(
    stocks_for_cc, checkout_for_cc
):
    lines = checkout_for_cc.lines.all()
    result = Warehouse.objects.applicable_for_click_and_collect(lines)
    result.get(click_and_collect_option=WarehouseClickAndCollectOption.ALL_WAREHOUSES)
    warehouse2 = result.get(
        click_and_collect_option=WarehouseClickAndCollectOption.LOCAL_STOCK
    )

    assert result.count() == 2
    assert warehouse2.stock_set.count() == lines.count()


def test_applicable_for_click_and_collect_quantity_exceeded_for_local(
    stocks_for_cc, checkout_for_cc
):
    lines = checkout_for_cc.lines.all()
    line = lines[2]
    line.quantity = 20
    line.save(update_fields=["quantity"])
    checkout_for_cc.refresh_from_db()

    result = Warehouse.objects.applicable_for_click_and_collect(lines)
    assert result.count() == 1
    with pytest.raises(Warehouse.DoesNotExist):
        result.get(click_and_collect_option=WarehouseClickAndCollectOption.LOCAL_STOCK)
