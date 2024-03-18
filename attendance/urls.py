from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
# router.register(r'attendance', AttendanceViewSet)
urlpatterns = router.urls
from django.urls import path
from . import views


urlpatterns = [
    path('api/check_in/<int:pk>/', views.check_in),
    path('api/check_out/<int:pk>/', views.check_out),
    # Other URLs
]+ router.urls