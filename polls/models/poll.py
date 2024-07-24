from django.db import models
from .category import Category
from .tag import Tag


class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    question = models.TextField()
    expiry_date = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='polls', blank=True)

    def __str__(self):
        return self.question

    class Meta:
        db_table = "poll"


class Choice(models.Model):
    id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text

    class Meta:
        db_table = "choice"
