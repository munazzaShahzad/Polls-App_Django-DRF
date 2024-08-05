from django.db import models
from django.core.validators import MinLengthValidator


class Tag(models.Model):
    """
    Tags to affiliate to a poll.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, validators=[MinLengthValidator(3)])

    def __str__(self):
        return str(self.id) + ': ' + str(self.name)

    class Meta:
        db_table = "tag"
