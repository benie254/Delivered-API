from django.shortcuts import render
from deliver_app.serializers import DeliverySerializer
from deliver_app.models import Delivery as Deliver, Dailycumulative, MonthlyCumulative
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework import status 
from rest_framework.response import Response
from decouple import config 
from django.template.loader import render_to_string
from twilio.rest import Client 
import datetime as dt
from django.db.models import F, ExpressionWrapper, DecimalField, PositiveIntegerField, Sum

# Create your views here.
@permission_classes([AllowAny,])
class Delivery(APIView):
    def post(self, request):
        serializer = DeliverySerializer(data=request.data)
        if serializer.is_valid():
            price_pl = serializer.validated_data['price_pl']
            amount = serializer.validated_data['amount']
            delivered_by = serializer.validated_data['delivered_by']
            delivery = serializer.save()
            delivery.dailycumulative.amount = serializer.validated_data['amount']
            delivery.dailycumulative.earned = 0.00
            delivery.save()
            delivery.refresh_from_db()
            msg = render_to_string('delivery-new.html', {
                'amount': amount,
                'delivered_by': delivered_by,
            })
            # account_sid = config('ACCOUNT_SID')
            # auth_token = config('AUTH_TOKEN')
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            #     body=msg,
            #     from_= config('TWILIO_FROM'),
            #     to= config('TWILIO_TO')
            # )
            status_code = status.HTTP_201_CREATED
            response = {
                'success' : 'True',
                'status code' : status_code,
                'message': 'Message sent  successfully',
                }
            # print(message.sid)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([AllowAny,])
class AllReports(APIView):
    def get(self, request, format=None):
        deliveries = Deliver.objects.all().order_by('-delivered')
        serializers = DeliverySerializer(deliveries,many=True)
        return Response(serializers.data)
    
@permission_classes([AllowAny,])
class Reports(APIView):
    def get(self, request, format=None):
        deliveries = Deliver.objects.all().order_by('-delivered')
        serializers = DeliverySerializer(deliveries,many=True)
        last_delivery = Deliver.objects.all().last()
        last_delivery.earned = ExpressionWrapper(F('price_pl') * F('amount'),output_field=DecimalField)
        last_delivery.save()
        last_delivery.refresh_from_db()
        return Response(serializers.data)
    
@permission_classes([AllowAny,])
class TodayReports(APIView):
    def get(self, request, format=None):
        today = dt.date.today()
        deliveries = Deliver.objects.all().filter(delivered=today).order_by('-delivered')
        serializers = DeliverySerializer(deliveries,many=True)
        return Response(serializers.data)
    
@permission_classes([AllowAny,])
class DailyCumulatives(APIView):
    def get(self, request, format=None):
        today = dt.date.today()
        today_deliveries = Deliver.objects.all().filter(delivered=today).order_by('-delivered')
        today_cumulative = Dailycumulative.objects.all().last()
        today_cumulative.earned = today_deliveries.aggregate(TOTAL = Sum('earned'))['TOTAL']
        today_cumulative.amount = today_deliveries.aggregate(TOTAL = Sum('amount'))['TOTAL']
        today_cumulative.save()
        today_cumulative.refresh_from_db()
        serializers = DeliverySerializer(today_cumulative,many=False)
        return Response(serializers.data)
    
    def post(self, request):
        serializer = DeliverySerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MonthlyCumulatives(APIView):
    def get(self, request, format=None):
        today = dt.datetime.now()
        month_deliveries = Deliver.objects.all().filter(delivered__month=today.month)
        month_cumulative = MonthlyCumulative.objects.all().last()
        month_cumulative.earned = month_deliveries.aggregate(TOTAL = Sum('earned'))['TOTAL']
        month_cumulative.amount = month_deliveries.aggregate(TOTAL = Sum('amount'))['TOTAL']
        month_cumulative.save()
        month_cumulative.refresh_from_db()
        serializers = DeliverySerializer(month_cumulative,many=False)
        return Response(serializers.data)