
from pyexpat import model
from xml.dom import ValidationErr
from attr import fields
from django.forms import ValidationError
from django.http import JsonResponse
from rest_framework import serializers
from license_api.models import UserDetails, LicenseKey, SubUser
from license_api.models import UpdateFile
from django.core.validators import validate_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = "__all__"

        def create(self, validated_data):
            try:
                license = LicenseKey.objects.create(**validated_data)
            except ValidationError:
                return JsonResponse({
                    "email": "Invalid email address"
                })

            return license

    def validate(self, attrs):
        if validate_email(attrs["email"]):
            raise ValidationError("Invalid email address")
        return super().validate(attrs)


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseKey
        fields = "__all__"

    def create(self, validated_data):
        return LicenseKey.objects.create(**validated_data)


class SubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubUser
        fields = "__all__"


class CheckLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseKey
        fields = ('key',)


class UpdateFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdateFile
        fields = "__all__"
