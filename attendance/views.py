from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Employee, Attendance,Department
from .serializers import EmployeeSerializer,DepartmentSerializer
import time
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

class EmployeeRegistrationView(APIView):
    
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        employee = Employee.objects.create(user=user)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class DepartmentView(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class EmployeeLoginView(APIView):
    AUTHENTICATION_CLASSES = []
    AUTHERIZARION_CLASSES = []
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class CheckInView(APIView):
    permission_classes = [IsAuthenticated]
   # check_in_list = []

    def post(self, request):
        employee = request.user.employee
        try:
            latest_attendance = Attendance.objects.filter(employee=employee).latest('check_in')
            if not latest_attendance.check_out:
                return Response({'error': 'Employee already checked in'}, status=status.HTTP_400_BAD_REQUEST)
        except Attendance.DoesNotExist:
            pass
        attendance = Attendance.objects.create(employee=employee)
        #check_in_list.append(timezone.now())
        return Response({'message': 'Checked in successfully'})

class CheckOutView(APIView):
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        employee = request.user.employee
        
        #check_out_list = []
        try:
            latest_attendance = Attendance.objects.filter(employee=employee).latest('check_in')
            if latest_attendance.check_out:
                return Response({'error': 'Employee already checked out'}, status=status.HTTP_400_BAD_REQUEST)
            latest_attendance.check_out = timezone.now()  # Use timezone.now() to get an offset-aware datetime
            #check_out_list.append(timezone.now())
            latest_attendance.save()
            
            check_in_time = latest_attendance.check_in.astimezone(timezone.get_current_timezone())  # Convert check_in_time to the project timezone
            check_out_time = timezone.make_aware(time.time.now(), timezone.get_current_timezone())  # Make check_out_time aware using Django's timezone
            
            # Calculate attendance hours
            attendance_hours = (check_out_time - check_in_time).total_seconds() / 3600
            if attendance_hours >= 9:
                status1 = 'Present'
            else:
                status1 = 'Absent'
            latest_attendance.status = status1
            latest_attendance.save()
            
            return Response({'message': 'Checked out successfully', 'status1': status1})
        except Attendance.DoesNotExist:
            return Response({'error': 'Employee has not checked in yet'}, status=status.HTTP_400_BAD_REQUEST)
