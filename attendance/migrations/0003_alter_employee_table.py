# Generated by Django 5.0.3 on 2024-03-28 11:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0002_alter_employee_phone_number"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="employee",
            table="Employee",
        ),
    ]