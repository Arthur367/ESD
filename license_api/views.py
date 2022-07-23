from ast import Not
from datetime import datetime, timedelta
from email import message
import json
from multiprocessing import context
from operator import sub
import re
from django import views
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.response import Response
from rest_framework import viewsets
from license_api.models import UserDetails, LicenseKey, SubUser, UpdateFile
from license_api.serializers import UserSerializer, CheckLicenseSerializer
from license_api.serializers import LicenseSerializer, SubUserSerializer
from license_api.serializers import UpdateFileSerializer
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import APIView
from license_api.forms import UserForm, AppForm
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.template.loader import get_template
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
            userData = request.data
            user_serializer = UserSerializer(data=userData)
            user = None
            print("Here")
            qs = UserDetails.objects.all()
            for exist in qs:
                if exist.companyName == userData["companyName"]:
                    return Response({"message": "Company Already Exists"},
                                    status=status.HTTP_400_BAD_REQUEST)
            if user_serializer.is_valid():
                user = user_serializer.save()
                maxUser = 0
                if userData["userNumbers"] == "":
                    maxUser = 1
                else:
                    maxUser = int(userData["userNumbers"])
                license = LicenseKey(
                    dateActivated=datetime.today().date(),
                    activatedTo=datetime.today() +
                    relativedelta(years=3),
                    maxUsers=maxUser
                )
                license.save()
                if user is not None:
                    users = UserDetails.objects.get(pk=user.id)
                    print("Users: ", user)
                    users.license = license
                    users.superUser = True
                    users.firstUse = True
                    users.save()
                    print("User> ", license, user.superUser)

                    return Response({"message": "Request Created.Please wait "
                                     "for LicenseKey in your mail"},
                                    status=status.HTTP_201_CREATED)
            return Response(user_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class LicenseViewSet(viewsets.ModelViewSet):
    queryset = LicenseKey.objects.all()
    serializer_class = LicenseSerializer


def home(request):
    qs = UpdateFile.objects.all()
    apps = UpdateFile.objects.count()
    users = UserDetails.objects.count()
    startdate = datetime.today().date()
    enddate = startdate + relativedelta(days=6)
    license = LicenseKey.objects.all()
    data_list = []
    for lic in license:
        number_of_users = lic.numberOfUsers
        data_list.append(number_of_users)
    total_users = sum(data_list)
    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES,)
        if form.is_valid():
            app = form.save(commit=False)
            app.uploadedDate = datetime.today().date()
            app.save()
            # uploadDate = UpdateFile(
            #     uploadedDate=datetime.datetime.today().date())
            # uploadDate.save()
            return redirect('dashboard')
    else:
        form = AppForm(request.FILES)
    context = {"form": form, "apps": qs, "number": apps,
               "users": users, "filter": total_users}

    return render(request, 'dashboard.html', context)


def table(request):
    context = {}
    qs = UserDetails.objects.all().order_by("fullName")
    paginator = Paginator(qs, 10)
    page = request.GET.get('page', 1)
    context["datas"] = qs
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return render(request, 'tables.html', {'users': users})


def update_license(request, pk):
    user = UserDetails.objects.get(pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if user.licenseActivated is False:
                message = get_template("deactivateEmail.html").render(
                    {
                        'users': user
                    })
                mail = EmailMessage(
                    subject="License Key Deactivated",
                    body=message,
                    to=[user.email],
                    reply_to=['arthurkin2019@gmail.com'],
                )
                mail.content_subtype = "html"
                mail.send(fail_silently=False)
                print("Email Sent")
            return redirect('table')
    else:
        form = UserForm(instance=user)
        main = SubUser.objects.filter(licenseKey=user.license)
        print(main)
        print(user.id)
    context = {"form": form, "userDetails": user,
               "subUser": main, "id": user.id}
    return render(request, 'profile.html', context)


def billing(request):
    return render(request, 'billing.html')


def notification(request):
    qs = UpdateFile.objects.all()
    apps = UpdateFile.objects.count()
    users = UserDetails.objects.count()
    context = {"apps": qs, "number": apps, "users": users}
    return render(request, 'notifications.html', context)


class SubUserViewSet(APIView):
    queryset = SubUser.objects.all()
    serializer_class = SubUserSerializer

    def get(self, request):
        qs = SubUser.objects.all()
        print(qs)
        seriliazer = SubUserSerializer(qs, many=True)
        return Response(data=seriliazer.data, status=status.HTTP_200_OK)

    def post(self, request):
        userData = request.data
        print("request")
        print(request.POST)
        print(userData['licenseKey'])
        try:
            license = LicenseKey.objects.filter(key=userData['licenseKey'])
            admin = UserDetails.objects.get(license=license.first())
        except LicenseKey.DoesNotExist:
            return Response({'message': 'No Such License Key'},
                            status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({'message': 'No Such License Key'},
                            status=status.HTTP_400_BAD_REQUEST)
        except UserDetails.DoesNotExist:
            return Response({'message': 'No Such User with this '
                             'License Key exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        print("admin")
        print(admin)
        if license.first().activated is True:
            if admin.licenseActivated is False:
                return Response({"message": "License Key Deactivated."
                                 " Please Contact AdminiStrator"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                if admin.subUser:
                    if datetime.today().date() <= license.first().activatedTo:
                        if admin.subUser.deviceID == userData['deviceID']:
                            return Response({'message': 'Welcome Back'},
                                            status=status.HTTP_200_OK)
                        else:
                            if license.first().maxUsers <= license.first().numberOfUsers:
                                return Response({'message': 'Max Users Already'
                                                 ' Reached update plan'},
                                                status=status.HTTP_400_BAD_REQUEST)
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
                            return Response({'message': 'Successfull'},
                                            status=status.HTTP_200_OK)
                    else:
                        return Response({"message": "License Expired. Please"
                                         " Renew."},
                                        status=status.HTTP_400_BAD_REQUEST)
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
                    return Response({'message': 'Successfull'},
                                    status=status.HTTP_200_OK)

        else:
            return Response({"message": "Please Wait for Original"
                             " User to Activate License"},
                            status=status.HTTP_400_BAD_REQUEST)


class CheckLicense(APIView):
    def post(self, request):
        userData = request.data
        print("request")
        print(request.data)
        print(userData['key'])
        try:
            license = LicenseKey.objects.filter(key=userData['key'])
            admin = UserDetails.objects.get(license=license.first())
        except LicenseKey.DoesNotExist:
            return Response({'message': 'No Such License Key'},
                            status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({'message': 'No Such License Key'},
                            status=status.HTTP_400_BAD_REQUEST)
        except UserDetails.DoesNotExist:
            return Response({'message': 'No Such User with these'
                             ' License Key exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        if datetime.today().date() <= license.first().activatedTo:
            if admin.firstUse is False:
                if admin.licenseActivated is False:
                    return Response({"message": "License Key Deactivated."
                                     " Please Contact AdminiStrator for"
                                     " Reactivation"},
                                    status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'Welcome Back'},
                                status=status.HTTP_200_OK)

            else:
                for lic in license:
                    lic.numberOfUsers += 1
                    lic.activated = True
                    lic.save()
                admin.firstUse = False
                admin.licenseActivated = True
                admin.save()
                return Response({'message': 'Successfull'},
                                status=status.HTTP_200_OK)
        else:
            return Response({"message": "License Key Expired, Please Renew"},
                            status=status.HTTP_400_BAD_REQUEST)


class UpdateFileViewSet(APIView):
    def get(self, request):
        qs = UpdateFile.objects.all()
        serializer = UpdateFileSerializer(qs, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        userData = request.data
        file_serializer = UpdateFileSerializer(data=userData)
        print(userData)
        upload = None
        if file_serializer.is_valid():
            upload = file_serializer.save()
            return Response({"message": "saved Successfully"},
                            status=status.HTTP_200_OK)
        else:
            return Response(file_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class CheckLicenseValidity(APIView):
    def get(self, request):
        qs = UserDetails.objects.all()
        print(qs)
        for a in qs:
            print("Name: ", a)
        seriliazer = UserSerializer(qs, many=True)
        users = {"users": seriliazer.data}
        return Response(data=users, status=status.HTTP_200_OK)

    def post(self, request):
        qs = UserDetails.objects.all()
        userData = request.data
        print(userData)
        try:
            license = LicenseKey.objects.filter(key=userData['key'])
            admin = UserDetails.objects.get(license=license.first())
        except LicenseKey.DoesNotExist:
            return Response({'message': 'No Such License Key'},
                            status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({'message': 'No Such License Key'},
                            status=status.HTTP_400_BAD_REQUEST)
        except UserDetails.DoesNotExist:
            return Response({'message': 'No Such User with this'
                             ' License Key exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        if license and admin:
            if admin.licenseActivated is True and datetime.today().date() <= license.first().activatedTo:
                return Response({"message": "Activated"},
                                status=status.HTTP_200_OK)
            else:
                return Response({"message": "License Key Deactivated Please"
                                 " Contact Administrator for Reactivation"},
                                status=status.HTTP_400_BAD_REQUEST)


def assignLicense(request, pk):
    user = UserDetails.objects.get(pk=pk)
    if request.method == 'POST':
        print(user)
        message = get_template("sendKey.html").render(
            {
                'users': user
            })
        mail = EmailMessage(
            subject="License Key Generation",
            body=message,
            to=[user.email],
            reply_to=['arthurkin2019@gmail.com'],
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=False)
        return JsonResponse({"message": "Mail Sent"},
                            status=status.HTTP_200_OK)
