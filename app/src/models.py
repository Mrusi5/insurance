from tortoise.models import Model
from tortoise import fields


class InsuranceEntry(Model):
    id = fields.IntField(pk=True)
    cargo_type = fields.CharField(max_length=255)
    declared_value = fields.DecimalField(max_digits=10, decimal_places=2)
    insurance_date = fields.DateField()
    request_date = fields.DatetimeField(auto_now_add=True)
    insurance_amount = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "insurance_entries"