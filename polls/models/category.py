from django.db import models
from django.core.validators import MinLengthValidator


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, validators=[MinLengthValidator(3)])

    def __str__(self):
        return self.name

    class Meta:
        db_table = "category"
