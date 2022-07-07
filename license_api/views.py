import datetime
import json
from multiprocessing import context
from operator import sub
from django import views
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.response import Response
from rest_framework import viewsets
from license_api.models import UserDetails, LicenseKey, SubUser
from license_api.serializers import UserSerializer
from license_api.serializers import LicenseSerializer, SubUserSerializer
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import APIView
from license_api.forms import UserForm
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import Context
from django.template.loader import get_template


# Create your views here.


class UserViewSet(APIView):
    queryset = UserDetails.objects.all()
    serializer_class = UserSerializer

    def get(self, request):
        qs = UserDetails.objects.all()
        print(qs)
        for a in qs:
            print("Name: ", a.fullName)
            print("License: ", a.license)

        seriliazer = UserSerializer(qs, many=True)
        return Response(data=seriliazer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.method == 'POST':
            userData = request.POST
            user_serializer = UserSerializer(data=userData)
            user = None
            print("Here")
            if user_serializer.is_valid():
                user = user_serializer.save()
                license = LicenseKey(
                    dateActivated=datetime.datetime.today().date(),
                    maxUsers=userData["userNumbers"]
                )
                license.save()

                if user is not None:
                    users = UserDetails.objects.get(pk=user.id)
                    print("Users: ", user)
                    users.license = license
                    users.save()
                    print("User> ", license)
                    message = get_template("sendKey.html").render(
                        {
                            'users': users
                        })
                    mail = EmailMessage(
                        subject="License Key Generation",
                        body=message,
                        to=[users.email],
                        reply_to=['arthurkin2019@gmail.com'],
                    )
                    mail.content_subtype = "html"
                    mail.send(fail_silently=False)
                return Response(user_serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(user_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class LicenseViewSet(viewsets.ModelViewSet):
    queryset = LicenseKey.objects.all()
    serializer_class = LicenseSerializer


def home(request):
    return render(request, 'dashboard.html')


def table(request):
    context = {}
    qs = UserDetails.objects.all()
    context["datas"] = qs
    return render(request, 'tables.html', context)


def update_license(request, pk):
    user = UserDetails.objects.get(pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('table')
    else:
        form = UserForm(instance=user)
        main = SubUser.objects.filter(licenseKey=user.license)
        print(main)
    context = {"form": form, "userDetails": user,
               "subUser": main}
    return render(request, 'profile.html', context)


def billing(request):
    return render(request, 'billing.html')


def notification(request):
    return render(request, 'notifications.html')


class SubUserViewSet(APIView):
    queryset = SubUser.objects.all()
    serializer_class = SubUserSerializer

    def get(self, request):
        qs = SubUser.objects.all()
        print(qs)
        seriliazer = SubUserSerializer(qs, many=True)
        return Response(data=seriliazer.data, status=status.HTTP_200_OK)

    def post(self, request):
        userData = request.POST
        print("request")
        print(request.POST)
        print(userData['licenseKey'])
        try:
            license = LicenseKey.objects.filter(key=userData['licenseKey'])
        except LicenseKey.DoesNotExist:
            return Response({'message': 'No Such License Key'})
        admin = UserDetails.objects.get(license=license.first())
        print("admin")
        print(admin)
        if admin.subUser.deviceID != userData['deviceID']:
            if license.first().maxUsers <= license.first().numberOfUsers:
                return Response({'message': 'Max Users Already Reached update plan'})
            else:
                for lic in license:
                    lic.numberOfUsers += 1
                    lic.save()
                subUser = SubUser(
                    deviceID=userData['deviceID'],
                    licenseKey=userData['licenseKey'],
                    isActive=True
                )
                subUser.save()
                admin.subUser = subUser
                admin.save()
                return Response({'message': 'Successfull'})

        else:
            return Response({'message': 'Welcome Back'})
