from django.shortcuts import render
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Employee, Attendance
from .serializers import *

# Create your views here.
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

from django.utils import timezone   
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def check_in(request, pk):
    try:
        employee = Employee.objects.get(pk=pk)
        attendance = Attendance(employee=employee)
        attendance.save()
        return Response({'message': 'Checked in successfully'}, status=status.HTTP_201_CREATED)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

from datetime import datetime
from pytz import timezone

@api_view(['POST'])
def check_out(request, pk):
    try:
        employee = Employee.objects.get(pk=pk)
        latest_attendance = Attendance.objects.filter(employee=employee).latest('check_in')
        if latest_attendance.check_out:
            return Response({'error': 'Employee already checked out'}, status=status.HTTP_400_BAD_REQUEST)
        
        ist = timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist)

        latest_attendance.check_out = current_time_ist
        latest_attendance.save()
        return Response({'message': 'Checked out successfully'}, status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    except Attendance.DoesNotExist:
        return Response({'error': 'Employee has not checked in yet'}, status=status.HTTP_400_BAD_REQUEST)
