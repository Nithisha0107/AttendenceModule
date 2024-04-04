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
            latest_attendance  = Attendance.objects.filter(employee=employee,date = today).latest('check_in')
            
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
    
from datetime import timedelta

class AttendanceView(APIView):
    def get(self, request):
        user = request.user
        employee = Employee.objects.get(user=user)
        start_date_string = request.query_params.get('from')
        end_date_string = request.query_params.get('to')
        
        # Check if both start_date and end_date are provided
        if not start_date_string or not end_date_string:
            return Response({'error': 'Both start_date and end_date are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse start_date and end_date strings into datetime objects
        start_date = datetime.strptime(start_date_string, "%d-%m-%Y").date()
        end_date = datetime.strptime(end_date_string, "%d-%m-%Y").date()
        
        # Initialize an empty list to store attendance records
        attendance_data = []

        # Loop through each date in the range
        current_date = start_date
        while current_date <= end_date:
            # Retrieve attendance records for the current date
            attendances_for_date = Attendance.objects.filter(employee=employee, date=current_date).order_by('check_in')
            
            # Initialize variables to calculate total working hours and break hours for the date
            total_working_hours = 0
            total_break_hours = 0
            check_in_time = None
            check_out_time = None
            previous_check_out_time = None
            for attendance in attendances_for_date:
                # Combine date and time to create datetime objects
                check_in_datetime = datetime.combine(current_date, attendance.check_in)
                check_out_datetime = datetime.combine(current_date, attendance.check_out)

                # Calculate duration worked
                duration_worked = (check_out_datetime - check_in_datetime).total_seconds() / 3600
                total_working_hours += duration_worked

                # If there was a previous check-out, calculate break duration
                if previous_check_out_time is not None:
                    break_duration = (check_in_datetime - previous_check_out_time).total_seconds() / 3600
                    total_break_hours += break_duration

                # Update previous check-out time
                previous_check_out_time = check_out_datetime
            
            
            status1 = "Present" if total_working_hours >= 9 else ("0.5 Present" if 4 <= total_working_hours < 9 else "Absent")


            total_working_hours_str = str(timedelta(hours=total_working_hours))
            total_break_hours_str = str(timedelta(hours=total_break_hours))
            # Append attendance data for the current date to the list
            attendance_data.append({
                'date': current_date,
                'check_in': attendances_for_date[0].check_in if attendances_for_date else None,
                'check_out': attendances_for_date[len(attendances_for_date) - 1].check_out if attendances_for_date else None,
                'break_hours': total_break_hours_str,
                'present_hours': total_working_hours_str,
                'status': status1
            })

            # Move to the next date
            current_date += timedelta(days=1)

        return Response({'attendance_data': attendance_data}, status=status.HTTP_200_OK)

        



