from email.policy import default
from random import choices
from uuid import uuid4
from django.db import models


# Create your models here.


class UserDetails(models.Model):
    PLANT_TYPES = (
        ('INDIVIDUAL', 'Individual'),
        ('GROUP', 'Group'),
        ('COMPANY', 'Company'),
    )

    fullName = models.CharField(max_length=100)
    companyName = models.CharField(max_length=100)
    contactPhone = models.CharField(max_length=10)
    email = models.CharField(max_length=100)
    licenseActivated = models.BooleanField(default=False)
    superUser = models.BooleanField(default=False)
    deviceId = models.CharField(max_length=100, null=True, blank=True)
    firstUse = models.BooleanField(default=True)
    userNumbers = models.PositiveIntegerField(
        default=1)
    license = models.ForeignKey(
        "LicenseKey", on_delete=models.CASCADE, null=True, blank=True)
    subUser = models.ForeignKey(
        "SubUser", on_delete=models.CASCADE, null=True, blank=True,
        related_name='users_sub')

    def __str__(self):
        return f"{self.fullName}"


class LicenseKey(models.Model):
    key = models.UUIDField(default=uuid4())
    dateActivated = models.DateField()
    activated = models.BooleanField(
        default=False
    )
    numberOfUsers = models.PositiveIntegerField(
        default=0
    )
    maxUsers = models.PositiveIntegerField(
        default=1
    )
    activatedTo = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.key}"


class SubUser(models.Model):
    deviceID = models.CharField(
        max_length=100, null=True, blank=True)
    licenseKey = models.CharField(max_length=100, null=True, blank=True)
    isActive = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.licenseKey


class UpdateFile(models.Model):
    appVersion = models.CharField(null=True, blank=True, max_length=50)
    appFile = models.FileField(upload_to='app')
