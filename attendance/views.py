from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Employee, Attendance,Department
from .serializers import EmployeeSerializer,DepartmentSerializer,AttendanceSerializer
from datetime import datetime
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
        today = datetime.today().date()
        try:
            latest_attendance = Attendance.objects.filter(employee=employee,date = today).latest('check_in')
            
            if not latest_attendance.check_out:
                return Response({'error': 'Employee already checked in'}, status=status.HTTP_400_BAD_REQUEST)
        except Attendance.DoesNotExist:
            pass
        check_in_time = datetime.now().time()
        Attendance.objects.create(employee=employee,date = today,check_in = check_in_time)
        
        return Response({'message': 'Checked in successfully'},status=status.HTTP_201_CREATED)

class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        employee = Employee.objects.get(user = user)
        today = datetime.today().date()
        
        try:
           
            latest_attendance = Attendance.objects.filter(employee=employee,date = today, check_out__isnull=True).latest('check_in')
            if latest_attendance.check_out:
                return Response({'error': 'Employee already checked out'}, status=status.HTTP_400_BAD_REQUEST)
        except Attendance.DoesNotExist:
            return Response({'error': 'You have not checked in yet'}, status=status.HTTP_400_BAD_REQUEST)
            
        latest_attendance.check_out = datetime.now().time()  
            
        latest_attendance.save()
            
            
        check_in_time = latest_attendance.check_in
        check_out_time =latest_attendance.check_out
        check_in_datetime = datetime.combine(datetime.today(), check_in_time)
        check_out_datetime = datetime.combine(datetime.today(), check_out_time)
        attendance_timedelta = check_out_datetime - check_in_datetime
        attendance_hours = attendance_timedelta.total_seconds() / 3600
        if attendance_hours >= 9:
            status1 = 'Present'
        else:
            status1 = 'Absent'
        latest_attendance.status = status1
        latest_attendance.duration = attendance_hours
        latest_attendance.save()
            
        return Response({'message': 'Checked out successfully', 'status1': status1},status=status.HTTP_201_CREATED)
# class AttendanceView(APIView):
#     def get(self,request):
#         #import pdb;pdb.set_trace()
#         import datetime
#         date =  datetime.date.today()
#         user = Employee.objects.get(user = request.user)
#         from django.db.models import Sum
 
#         #ata = Attendance.objects.filter(date=date, employee_id=user).aggregate(total_hours_spent=Sum('duration'))
 
#         # = Attendance.objects.filter(date=date, employee_id=user).values('employee_id', 'date').annotate(total_hours_spent=Sum('duration'))
#         result = Attendance.objects.filter(date=date, employee_id=user).values('date', 'employee_id').annotate(total_hours_spent=Sum('duration')).get()
#         if result['total_hours_spent'] is None:
#             status1 = 'Absent'
 
#         else :
#             attendance_hours = (result["total_hours_spent"]) /  (3600 * 1000)
#             if attendance_hours >= 9:
#                 status1 = 'Present'
#             else:
#                 status1 = 'Absent'
           
#         data = AttendanceSerializer(result)
#         res = data.data
       
#         return Response({"data":data.data,"status1":status1})
        
class  AttendanceView(APIView):


    def get(self,request):
        #import pdb;pdb.set_trace()
        user = request.user
        employee = Employee.objects.get(user=user)
        
        # # Get today's date
        # today = datetime.today().date()

        
        date_string = request.query_params.get('date')
        month_string = request.query_params.get('month')
       
        
       
        if date_string :
            date_object = datetime.strptime(date_string, "%d-%m-%Y")
            attendances_today = Attendance.objects.filter(employee=employee, date=date_object)

        else :
            date_object = int(month_string)
            attendances_today = Attendance.objects.filter(employee=employee, date__month=date_object)

        
        # Get all attendance records for the employee for today
        
        
        
        # Calculate total working hours for the day
        total_working_hours = sum([attendance.duration for attendance in attendances_today if attendance.duration])
        
        # Determine the status based on total working hours
        status1 = 'Present' if total_working_hours >= 9 else 'Absent'
        
        # Update status for all attendance records for today
        for attendance in attendances_today:
            attendance.status = status
            attendance.save()
        
        return Response({'status1': status1, 'total_working_hours': total_working_hours}, status=status.HTTP_200_OK)

class AttendaceMonthlyReport(APIView):
    def get(self,request):
        pass