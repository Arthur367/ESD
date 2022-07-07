
from rest_framework import serializers
from license_api.models import UserDetails, LicenseKey, SubUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = "__all__"

        def create(self, validated_data):
            return LicenseKey.objects.create(**validated_data)


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseKey
        fields = ('dateActivated', 'activated', 'numberOfUsers',
                  'maxUsers', 'activatedTo', )

    def create(self, validated_data):
        return LicenseKey.objects.create(**validated_data)


class SubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubUser
        fields = "__all__"
