from django.urls import path, include
from esdAuth.views import login

urlpatterns = [
    path('login/', login, name='login')
]
