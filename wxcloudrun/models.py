from django.db import models

class Counters(models.Model):
    id = models.AutoField(primary_key=True)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'counters'
