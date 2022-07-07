from django import views
from django.db import router
from django.urls import include, path
from rest_framework import routers
from license_api.views import UserViewSet, LicenseViewSet, SubUserViewSet
from license_api.views import home, table, billing, notification, update_license
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
    path('subUser/', SubUserViewSet.as_view())
]
