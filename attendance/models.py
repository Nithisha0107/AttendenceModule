from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
class Department(models.Model):
    technology = models.CharField(max_length = 20,unique = True)

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #department = models.ForeignKey(Department,on_delete = models.CASCADE)
    #First_name = models.CharField(max_length=50)
    #Last_name = models.CharField(max_length=50)
    #email = models.EmailField()
    #phone_number = models.IntegerField()
    # Add other employee fields as needed

    def __str__(self):
        return self.user.username

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add =True,null = True)
    check_in = models.TimeField(auto_now_add=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10,blank =True)
    duration = models.GeneratedField( expression=F("check_out") - F("check_in"),
        output_field=models.FloatField(),
        db_persist=True,)
    def __str__(self):
        return f"{self.employee} - {self.check_in} to {self.check_out}"
    
    
