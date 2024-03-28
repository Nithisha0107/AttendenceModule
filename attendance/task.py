# tasks.py
from celery import shared_task

from .models import Employee

@shared_task
def send_email_task(email):
    # Your task logic here
    emp = Employee(username="lakshmi kanth",password="Lucky")
    emp.save()
    return
