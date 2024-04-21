from django.db import migrations, models

import weenspace.core.utils.json_serializer


class Migration(migrations.Migration):
    dependencies = [
        ("discount", "0063_basediscount_voucher_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="promotionrule",
            name="catalogue_predicate",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=weenspace.core.utils.json_serializer.CustomJsonEncoder,
            ),
        ),
    ]
