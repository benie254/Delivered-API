from django.shortcuts import render
from deliver_app.serializers import DeliverySerializer, DailyCumulativeSerializer, MonthlyCumulativeSerializer
from deliver_app.models import Delivery as Deliver, Dailycumulative, Monthlycumulative
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
import sendgrid
from sendgrid.helpers.mail import *
from deliver_app.utils import render_to_pdf 
import os
import pytz
from django.utils import timezone

# Create your views here.
@permission_classes([AllowAny,])
class Delivery(APIView):
    def post(self, request):
        serializer = DeliverySerializer(data=request.data)
        if serializer.is_valid():
            price_pl = serializer.validated_data['price_pl']
            amount = serializer.validated_data['amount']
            delivered_by = serializer.validated_data['delivered_by']
            received_from = serializer.validated_data['received_from']
            mobile = serializer.validated_data['mobile']
            location = serializer.validated_data['location']
            delivery = serializer.save()
            delivery.dailycumulative.amount = 0.00
            delivery.dailycumulative.earned = 0.00
            delivery.monthlycumulative.amount = 0.00
            delivery.monthlycumulative.earned = 0.00
            delivery.save()
            delivery.refresh_from_db()
            msg = render_to_string('delivery-new.html', {
                'price_pl': price_pl,
                'amount': amount,
                'delivered_by': delivered_by,
                'received_from': received_from,
                'mobile': mobile,
                'location': location
            })
            account_sid = os.environ["TWILIO_ACCOUNT_SID"]
            auth_token = os.environ["TWILIO_AUTH_TOKEN"]
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=msg,
                from_= config('TWILIO_FROM'),
                to= config('TWILIO_TO')
            )
            print(message.sid)
            status_code = status.HTTP_201_CREATED
            response = {
                'success' : 'True',
                'status code' : status_code,
                'message': 'Message sent  successfully',
                }
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsAuthenticated,])
class AllReports(APIView):
    def get(self, request, format=None):
        deliveries = Deliver.objects.all().order_by('-time')
        serializers = DeliverySerializer(deliveries,many=True)
        return Response(serializers.data)
    
@permission_classes([AllowAny,])
class Reports(APIView):
    def get(self, request, format=None):
        deliveries = Deliver.objects.all().order_by('-time')
        serializers = DeliverySerializer(deliveries,many=True)
        last_delivery = Deliver.objects.all().last()
        last_delivery.earned = ExpressionWrapper(F('price_pl') * F('amount'),output_field=DecimalField)
        last_delivery.save()
        last_delivery.refresh_from_db()
        return Response(serializers.data)
    
@permission_classes([IsAuthenticated,])
class TodayReports(APIView):
    def get(self, request, format=None):
        today = timezone.now()
        print(today)
        deliveries = Deliver.objects.all().order_by('-time').filter(delivered=today)
        serializers = DeliverySerializer(deliveries,many=True)
        return Response(serializers.data)

@permission_classes([IsAuthenticated,])
class DeleteReport(APIView):
    def delete(self, request, id, format=None):
        report = Deliver.objects.all().filter(pk=id).last()
        report.delete()
        return Response(status=status.HTTP_200_OK) 
    
@permission_classes([AllowAny,])
class DailyCumulatives(APIView):
    def get(self, request, format=None):
        today = dt.date.today()
        today_deliveries = Deliver.objects.all().filter(delivered=today)
        today_cumulative = Dailycumulative.objects.all().last()
        if today_cumulative:
            today_cumulative.earned = today_deliveries.aggregate(TOTAL = Sum('earned'))['TOTAL']
            today_cumulative.amount = today_deliveries.aggregate(TOTAL = Sum('amount'))['TOTAL']
            today_cumulative.save()
            today_cumulative.refresh_from_db()
            serializers = DeliverySerializer(today_cumulative,many=False)
            return Response(serializers.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

@permission_classes([IsAuthenticated,])
class DeleteDailyCumulative(APIView):
    def delete(self, request, id, format=None):
        report = Dailycumulative.objects.all().filter(pk=id).last()
        report.delete()
        return Response(status=status.HTTP_200_OK) 

@permission_classes([IsAuthenticated,])
class MonthlyCumulatives(APIView):
    def get(self, request, format=None):
        today = dt.datetime.now()
        month_deliveries = Deliver.objects.all().filter(delivered__month=today.month)
        month_cumulative = Monthlycumulative.objects.all().last()
        if month_cumulative:
            month_cumulative.earned = month_deliveries.aggregate(TOTAL = Sum('earned'))['TOTAL']
            month_cumulative.amount = month_deliveries.aggregate(TOTAL = Sum('amount'))['TOTAL']
            month_cumulative.save()
            month_cumulative.refresh_from_db()
            serializers = DeliverySerializer(month_cumulative,many=False)
            return Response(serializers.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

@permission_classes([IsAuthenticated,])
class DeleteMonthlyCumulative(APIView):
    def delete(self, request, id, format=None):
        report = Monthlycumulative.objects.all().filter(pk=id).last()
        report.delete()
        return Response(status=status.HTTP_200_OK) 

@permission_classes([IsAuthenticated,])
class EmailDailyCumulative(APIView):
    def post(self, request):
        serializer = DailyCumulativeSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            earned = serializer.validated_data['earned']
            day = serializer.validated_data['day']
            report = serializer.save()
            report.refresh_from_db()
            sg = sendgrid.SendGridAPIClient(api_key=config('SENDGRID_API_KEY'))
            msg = render_to_string('email/cumulative-daily.html', {
                'amount': amount,
                'earned': earned,
                'day': day,
            })
            message = Mail(
                from_email = Email("davinci.monalissa@gmail.com"),
                to_emails = "davinci.monalissa2@gmail.com",
                subject = "Daily Cumulative Report",
                html_content = msg
            )
            try:
                sendgrid_client = sendgrid.SendGridAPIClient(config('SENDGRID_API_KEY'))
                response = sendgrid_client.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)
            status_code = status.HTTP_201_CREATED
            response = {
                'success' : 'True',
                'status code' : status_code,
                'message': 'Daily cumulative report sent successfully',
                }
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated,])
class EmailMonthlyCumulative(APIView):
    def post(self, request):
        serializer = MonthlyCumulativeSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            earned = serializer.validated_data['earned']
            month = serializer.validated_data['month']
            report = serializer.save()
            report.refresh_from_db()
            sg = sendgrid.SendGridAPIClient(api_key=config('SENDGRID_API_KEY'))
            msg = render_to_string('email/cumulative-monthly.html', {
                'amount': amount,
                'earned': earned,
                'month': month,
            })
            message = Mail(
                from_email = Email("davinci.monalissa@gmail.com"),
                to_emails = "davinci.monalissa2@gmail.com",
                subject = "Monthly Cumulative Report",
                html_content = msg
            )
            try:
                sendgrid_client = sendgrid.SendGridAPIClient(config('SENDGRID_API_KEY'))
                response = sendgrid_client.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)
            status_code = status.HTTP_201_CREATED
            response = {
                'success' : 'True',
                'status code' : status_code,
                'message': 'Monthly cumulative report sent successfully',
                }
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)