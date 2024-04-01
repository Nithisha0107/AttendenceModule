from rest_framework.views import APIView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Employee, Attendance,Department
from .serializers import EmployeeSerializer,DepartmentSerializer,AttendanceSerializer
from datetime import datetime
from django.core.mail import send_mail
from django.http import Http404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

class DepartmentView(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class EmployeeRegistrationView(APIView):
    
    
    def post(self, request):
        # Extract data from the request
        department_id = request.data.get('department')
        username = request.data.get('username')
        password = request.data.get('password')
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        
        # Check if any required fields are missing
        if not department_id or not username or not password or not phone_number or not email:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password, email=email)
        employee = Employee.objects.create(user=user, phone_number=phone_number, email=email, department_id=department_id)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


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
        
class ForgotPasswordView(APIView):
    def generate_password_reset_token(self, employee):
        # Generate a password reset token using Django's default token generator
        uid = urlsafe_base64_encode(force_bytes(employee.pk))
        token = default_token_generator.make_token(employee)
        return f"{uid}-{token}"
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email address is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = Employee.objects.get(email=email)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee with this email address does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate a password reset token (you may need to implement this logic)
        token = self.generate_password_reset_token(employee)
        
        # Build the password reset link
        reset_link = f"http://your-domain.com/reset-password/?token={token}"
        
        # Send the password reset email
        send_mail(
            'Password Reset',
            f'Click the following link to reset your password: {reset_link}',
            'from@example.com',
            [email],
            fail_silently=False,
        )
        
        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({'error': 'Old password and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user.check_password(old_password):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

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
        
class  AttendanceView(APIView):

<<<<<<< HEAD
    # def get(self,request):
    #     user = request.user
    #     employee = Employee.objects.get(user=user)
    #     today = datetime.today().date()
    #     attendances_today = Attendance.objects.filter(employee=employee, date=today)
    #     total_working_hours = sum([attendance.duration for attendance in attendances_today if attendance.duration])
    #     status1 = 'Present' if total_working_hours >= 9 else 'Absent'
    #     for attendance in attendances_today:
    #         attendance.status = status
    #         attendance.save()
        
    #     return Response({'status1': status1, 'total_working_hours': total_working_hours}, status=status.HTTP_200_OK)
    def get(self, request, start_date, end_date):
        try:
            import pdb;pdb.set_trace()
            # Convert start_date and end_date strings to datetime objects
            start_date = datetime.strptime(start_date, '%d-%m-%Y').date()  # Assuming calendar format is 'dd-mm-yyyy'
            end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
            
            # Get the authenticated user (employee)
            user = request.user
            employee = Employee.objects.get(user=user)
            
            # Retrieve attendance records for the employee within the specified date range
            attendance_records = Attendance.objects.filter(employee=employee, date__range=[start_date, end_date])
            total_hours_worked = 0
            for attendance in attendance_records:
                if attendance.check_out:
                    # Combine date and time to create datetime objects
                    check_in_datetime = datetime.combine(attendance.date, attendance.check_in)
                    check_out_datetime = datetime.combine(attendance.date, attendance.check_out)
                    
                    # Calculate duration worked
                    duration_worked = (check_out_datetime - check_in_datetime).total_seconds() / 3600
                    total_hours_worked += duration_worked
            
            # Determine status based on total hours worked
            status = 'Present' if total_hours_worked >= 9 else 'Absent'
            
            # Update status for all attendance records
            for attendance in attendance_records:
                attendance.status = status
                attendance.save()
            # Serialize the attendance records
            serialized_data = []  # List to hold serialized data for each attendance record
            for attendance in attendance_records:
                serialized_data.append({
                    'date': attendance.date,
                    'check_in': attendance.check_in,
                    'check_out': attendance.check_out,
                    'status': attendance.status,
                    # Include other fields you want to display
                })
            
            return Response(serialized_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)})
=======

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
>>>>>>> ee6669e8bf4eb3ac5b9f8b37022b8bd249b81e35
