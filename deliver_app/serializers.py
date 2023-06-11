from rest_framework import serializers 
from deliver_app.models import Delivery, DailyCumulative, MonthlyCumulative

# serializers here
class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ('__all__')

class DailyCumulativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyCumulative
        fields = ('__all__')

class MonthlyCumulativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyCumulative
        fields = ('__all__')