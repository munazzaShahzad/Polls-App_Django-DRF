from django.db import models
from django.core.validators import MinLengthValidator


class Category(models.Model):
    """
    Defines a category for polls.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100, validators=[MinLengthValidator(3)])

    def __str__(self):
        return str(self.id) + ': ' + str(self.name)

    class Meta:
        db_table = "category"
        verbose_name_plural = "Categories"
