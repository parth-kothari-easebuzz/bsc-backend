import datetime
from rest_framework import serializers

from bscBhavCopy.models import BhavcopyRecord

class BhavcopyRecordSerializer(serializers.ModelSerializer):

    class Meta:

        model = BhavcopyRecord

        fields = ['id','trad_date','biz_date', 'name', 'open_price', 'close_price', 'high_price', 'low_price', 'created_date']

    def update(self, instance, data):
        data["modified_date"] = datetime.datetime.now()
        return super().update(instance, data)