import datetime
from django.db import models

# Create your models here.
class BhavcopyRecord(models.Model):
    trad_date = models.DateField(null=True)
    biz_date = models.DateField(null=True)
    name = models.CharField(null=True, max_length=200)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(default=datetime.datetime.now)
    modified_date = models.DateTimeField(default=datetime.datetime.now) 
    is_deleted = models.BooleanField(default=False)