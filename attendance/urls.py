from django.urls import path
from .views import EmployeeRegistrationView, EmployeeLoginView, CheckInView, CheckOutView,DepartmentView,AttendanceView
from rest_framework.routers import DefaultRouter
from .views import AttendaceMonthlyReport
router = DefaultRouter()
router.register(r'api/department',DepartmentView,basename='department')
urlpatterns = [
   # path('department/',DepartmentView.as_view(),name='employee-department'),
    path('api/register/', EmployeeRegistrationView.as_view(), name='employee-register'),
    path('api/login/', EmployeeLoginView.as_view(), name='employee-login'),
    path('api/checkin/', CheckInView.as_view(), name='checkin'),
    path('api/checkout/', CheckOutView.as_view(), name='checkout'),
    path('api/attendance/',AttendanceView.as_view(),name = 'employee_attendance'),
    path('api/attendace/<str:date>',AttendaceMonthlyReport.as_view() , name = "att"),
    # Other URLs
]+ router.urls
