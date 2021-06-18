import pytest

from saleor.warehouse import WarehouseClickAndCollectOption

from ...shipping.models import ShippingZone
from ..models import Stock, Warehouse


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


def test_applicable_for_click_and_collect_finds_warehouse_with_all_and_local(
    stocks_for_cc, checkout_with_lines
):
    expected_number_of_warehouses = 2

    lines = checkout_with_lines.lines.all()
    result = Warehouse.objects.applicable_for_click_and_collect(lines)
    result.get(click_and_collect_option=WarehouseClickAndCollectOption.ALL_WAREHOUSES)
    warehouse2 = result.get(
        click_and_collect_option=WarehouseClickAndCollectOption.LOCAL_STOCK
    )

    assert result.count() == expected_number_of_warehouses
    assert warehouse2.stock_set.count() == lines.count()


def test_applicable_for_click_and_collect_quantity_exceeded_for_local(
    stocks_for_cc, checkout_with_lines
):
    expected_number_of_warehouses = 1
    quantity_above_available_in_stock = 20

    lines = checkout_with_lines.lines.all()
    line = lines[2]
    line.quantity = quantity_above_available_in_stock
    line.save(update_fields=["quantity"])
    checkout_with_lines.refresh_from_db()

    result = Warehouse.objects.applicable_for_click_and_collect(lines)
    assert result.count() == expected_number_of_warehouses
    with pytest.raises(Warehouse.DoesNotExist):
        result.get(click_and_collect_option=WarehouseClickAndCollectOption.LOCAL_STOCK)


def test_applicable_for_click_and_collect_for_one_line_two_local_warehouses(
    stocks_for_cc, checkout_for_cc_one_line
):
    expected_total_number_of_warehouses = 3
    expected_total_number_of_local_warehouses = 2
    expected_total_number_of_all_warehouses = (
        expected_total_number_of_warehouses - expected_total_number_of_local_warehouses
    )

    lines = checkout_for_cc_one_line.lines.all()
    result = Warehouse.objects.applicable_for_click_and_collect(lines)
    assert result.count() == expected_total_number_of_warehouses
    assert (
        result.filter(
            click_and_collect_option=WarehouseClickAndCollectOption.LOCAL_STOCK
        ).count()
        == expected_total_number_of_local_warehouses
    )
    assert (
        result.filter(
            click_and_collect_option=WarehouseClickAndCollectOption.ALL_WAREHOUSES
        ).count()
        == expected_total_number_of_all_warehouses
    )


def test_applicable_for_click_and_collect_does_not_show_warehouses_with_empty_stocks(
    stocks_for_cc, checkout_with_lines
):
    expected_total_number_of_warehouses = 1
    reduced_stock_quantity = 0

    lines = checkout_with_lines.lines.all()
    stock = Stock.objects.filter(
        warehouse__click_and_collect_option=WarehouseClickAndCollectOption.LOCAL_STOCK
    ).last()
    stock.quantity = reduced_stock_quantity
    stock.save(update_fields=["quantity"])

    result = Warehouse.objects.applicable_for_click_and_collect(lines)
    assert result.count() == expected_total_number_of_warehouses
    assert (
        result.first().click_and_collect_option
        == WarehouseClickAndCollectOption.ALL_WAREHOUSES
    )


def test_applicable_for_click_and_collect_additional_stock_does_not_change_availbility(
    stocks_for_cc, checkout_with_lines, warehouses_for_cc, product_variant_list
):
    expected_total_number_of_stocks = 4
    expected_total_number_of_warehouses = 2
    expected_number_of_checkout_lines = 3

    Stock.objects.create(
        warehouse=warehouses_for_cc[3], product_variant=product_variant_list[3]
    )
    lines = checkout_with_lines.lines.all()

    result = Warehouse.objects.applicable_for_click_and_collect(lines)

    assert result.count() == expected_total_number_of_warehouses
    result.get(click_and_collect_option=WarehouseClickAndCollectOption.ALL_WAREHOUSES)
    warehouse = result.get(
        click_and_collect_option=WarehouseClickAndCollectOption.LOCAL_STOCK
    )
    assert warehouse.stock_set.count() == expected_total_number_of_stocks
    assert lines.count() == expected_number_of_checkout_lines
