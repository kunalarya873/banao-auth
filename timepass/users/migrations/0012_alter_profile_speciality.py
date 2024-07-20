# Generated by Django 5.0.7 on 2024-07-19 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_profile_speciality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='speciality',
            field=models.CharField(blank=True, choices=[('Cardiology', 'Cardiology'), ('Dermatology', 'Dermatology'), ('Neurology', 'Neurology'), ('Pediatrics', 'Pediatrics'), ('Ortho', 'Ortho'), ('Trauma', 'Trauma'), ('General Surgery', 'General Surgery')], max_length=100, null=True),
        ),
    ]