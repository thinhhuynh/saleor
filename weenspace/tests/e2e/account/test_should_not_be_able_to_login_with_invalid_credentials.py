import pytest

from ..shop.utils import prepare_shop
from ..utils import assign_permissions
from .utils import account_register, raw_token_create


@pytest.mark.e2e
def test_should_not_be_able_to_login_with_invalid_credentials_core_1506(
    e2e_not_logged_api_client,
    e2e_staff_api_client,
    permission_manage_product_types_and_attributes,
    shop_permissions,
):
    # Before
    permissions = [
        permission_manage_product_types_and_attributes,
        *shop_permissions,
    ]
    assign_permissions(e2e_staff_api_client, permissions)

    shop_data, _tax_config = prepare_shop(
        e2e_staff_api_client,
        channels=[
            {
                "shipping_zones": [
                    {
                        "shipping_methods": [
                            {},
                        ],
                    },
                ],
                "order_settings": {},
            }
        ],
        shop_settings={
            "enableAccountConfirmationByEmail": False,
        },
    )
    channel_slug = shop_data[0]["slug"]
    user_email = "user1@weenspace.com"
    user_password = "Test1234!"

    # Step 1 - Create account for the new customer
    user_account = account_register(
        e2e_not_logged_api_client,
        user_email,
        user_password,
        channel_slug,
    )
    user_id = user_account["user"]["id"]
    assert user_id is not None
    assert user_account["user"]["isActive"] is True

    # Step 2 - Login with invalid password
    invalid_password = "password"
    login_data = raw_token_create(
        e2e_not_logged_api_client, user_email, invalid_password
    )
    error = login_data["data"]["tokenCreate"]["errors"][0]
    assert error["field"] == "email"
    assert error["message"] == "Please, enter valid credentials"
    assert error["code"] == "INVALID_CREDENTIALS"

    # Step 3 - Login with invalid email
    invalid_email = "invalid@email.com"
    login_data = raw_token_create(
        e2e_not_logged_api_client, invalid_email, user_password
    )
    error = login_data["data"]["tokenCreate"]["errors"][0]
    assert error["field"] == "email"
    assert error["message"] == "Please, enter valid credentials"
    assert error["code"] == "INVALID_CREDENTIALS"
