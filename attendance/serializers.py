from rest_framework import serializers
from .models import Employee,Department,Attendance

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"  # Add other fields as needed

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields= "__all__"


