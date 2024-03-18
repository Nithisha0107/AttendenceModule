from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Present')  

# from django.db import models
# from django.contrib.auth.models import User
# import datetime
# # Create your models here.


# class Department(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.TextField()

# class Employee(models.Model):
#     user = models.OneToOneField(User,on_delete = models.PROTECT)
#     department = models.ForeignKey(Department,on_delete = models.PROTECT)
#     position = models.CharField(max_length=100)
#     monthly_leave_entitlement = models.IntegerField(default=1)  # Total number of leaves entitled per month

#     def remaining_leaves(self):
#         current_month = datetime.now().month
#         current_month_leave_taken = Leave.objects.filter(employee=self, start_date__month=current_month).count()

#         # Calculate remaining leaves for the current month
#         remaining_leaves_current_month = max(0, self.monthly_leave_entitlement - current_month_leave_taken)

#         # Check if employee has unused leave entitlement from the previous month
#         previous_month = current_month - 1 if current_month != 1 else 12  # Handle January
#         previous_month_leave_taken = Leave.objects.filter(employee=self, start_date__month=previous_month).count()
#         unused_leave_previous_month = max(0, self.monthly_leave_entitlement - previous_month_leave_taken)

#         # Combine remaining leaves for the current month and unused leave from the previous month
#         remaining_leaves = remaining_leaves_current_month + unused_leave_previous_month
#         return remaining_leaves

# class AttendanceRecord(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     date = models.DateField()
#     clock_in = models.DateTimeField()
#     clock_out = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(max_length=10, choices=(('Present', 'Present'), ('Absent', 'Absent')), default='Absent')
#     def calculate_status(self):
#         if self.clock_out:
#             duration = self.clock_out - self.clock_in
#             hours = duration.total_seconds() / 3600
#             if hours >= 9:
#                 return 'Present'
#         return 'Absent'

#     def save(self, *args, **kwargs):
#         if not self.pk:
#             self.status = self.calculate_status()
#         super().save(*args, **kwargs)

# class AttendanceReport(models.Model):
#     TIME_PERIOD_CHOICES = (
#         ('yearly', 'Yearly'),
#         ('monthly', 'Monthly'),
#     )
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     time_period = models.CharField(max_length=10, choices=TIME_PERIOD_CHOICES)
#     year = models.PositiveIntegerField()
#     month = models.PositiveIntegerField(null=True, blank=True)
#     present_days = models.PositiveIntegerField(default=0)
#     absent_days = models.PositiveIntegerField(default=0)
#     data = models.TextField()

#     def __str__(self):
#         return f"{self.employee.user.username} - {self.time_period} Report - Year: {self.year}"

#     def update_present_absent_days(self):
#         """
#         Update the total present and absent days based on the corresponding AttendanceRecord records.
#         """
#         if self.time_period == 'monthly':
#             # Filter AttendanceRecord instances for the specified employee, year, and month
#             attendance_records = AttendanceRecord.objects.filter(employee=self.employee, date__year=self.year, date__month=self.month)
#             # Count present and absent days
#             self.present_days = sum(1 for record in attendance_records if record.calculate_status() == 'Present')
#             self.absent_days = sum(1 for record in attendance_records if record.calculate_status() == 'Absent')
#         elif self.time_period == 'yearly':
#             # Filter AttendanceRecord instances for the specified employee and year
#             attendance_records = AttendanceRecord.objects.filter(employee=self.employee, date__year=self.year)
#             # Count present and absent days
#             self.present_days = sum(1 for record in attendance_records if record.calculate_status() == 'Present')
#             self.absent_days = sum(1 for record in attendance_records if record.calculate_status() == 'Absent')

# class Holiday(models.Model):
#     name = models.CharField(max_length=200)
#     date = models.DateField()

# class Leave(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     holiday = models.ForeignKey(Holiday, on_delete=models.SET_NULL, null=True, blank=True)
#     status = models.CharField(max_length=20, choices=(
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected')
#     ), default='pending')

#     def save(self, *args, **kwargs):
#         if self.pk:  # Check if the instance already exists (i.e., being updated)
#             old_instance = Leave.objects.get(pk=self.pk)
#             if self.status != old_instance.status:  # Check if the status has changed
#                 # Status has changed, update it in the database
#                 super().save(*args, **kwargs)
#                 # Here you can perform any additional actions you need
#         else:
#             super().save(*args, **kwargs)


# class Regularization(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     date = models.DateField()
#     clock_in = models.DateTimeField()
#     clock_out = models.DateTimeField()
#     reason = models.TextField()
#     status = models.CharField(max_length=20, choices=(
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected')
#     ), default='pending')

    
#     def save(self, *args, **kwargs):
#         if self.pk:  # Check if the instance already exists (i.e., being updated)
#             old_instance = Regularization.objects.get(pk=self.pk)
#             if self.status != old_instance.status:  # Check if the status has changed
#                 # Status has changed, update it in the database
#                 super().save(*args, **kwargs)
#                 # Here you can perform any additional actions you need
#         else:
#             super().save(*args, **kwargs)



