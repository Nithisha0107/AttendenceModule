from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Attendance
from django.urls import reverse

class CheckInViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_check_in_success(self):
        url = reverse('checkin')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Attendance.objects.filter(employee=self.user.employee).count(), 1)

    def test_already_checked_in(self):
        # Create an attendance object to simulate already checked in
        Attendance.objects.create(employee=self.user.employee)
        
        url = reverse('checkin')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Employee already checked in')
        self.assertEqual(Attendance.objects.filter(employee=self.user.employee).count(), 1)

    def test_multiple_check_in_success(self):
        # Create an attendance object with check out time to simulate previous check out
        Attendance.objects.create(employee=self.user.employee, check_out='2024-03-22 08:00:00')

        url = reverse('checkin')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Attendance.objects.filter(employee=self.user.employee).count(), 2)
