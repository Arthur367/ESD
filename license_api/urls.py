from os import name
from django import views
from django.db import router
from django.urls import include, path
from rest_framework import routers
from license_api.views import UserViewSet, LicenseViewSet, SubUserViewSet
from license_api.views import home, table, billing, notification
from license_api.views import CheckLicense, update_license, UpdateFileViewSet
from license_api.views import CheckLicenseValidity, assignLicense
router = routers.DefaultRouter()
# router.register(r'users', UserViewSet.as_view())

router.register(r'license', LicenseViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserViewSet.as_view()),
    path('dashboard/', home, name='dashboard'),
    path('tables/', table, name="table"),
    path('billing/', billing, name="billing"),
    path('notifications/', notification, name="notifications"),
    # path('profile/', profile, name='profile'),
    path('profile/<int:pk>', update_license, name='profile'),
    path('subUser/', SubUserViewSet.as_view()),
    path('check/', CheckLicense.as_view()),
    path('update/', UpdateFileViewSet.as_view()),
    path('getUsers/', CheckLicenseValidity.as_view()),
    path('assignLicense/<int:pk>', assignLicense, name="assign")
]
