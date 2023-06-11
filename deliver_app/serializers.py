from rest_framework import serializers 
from deliver_app.models import Delivery, Dailycumulative, Monthlycumulative

# serializers here
class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ('__all__')

class DailyCumulativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dailycumulative
        fields = ('__all__')

class MonthlyCumulativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monthlycumulative
        fields = ('__all__')