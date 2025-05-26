from django.urls import path
from . import views

urlpatterns = [

    path('', views.index),
    path('upload_code', views.upload_code),
    path('upload_zip', views.upload_zip),
    path('upload_page', views.upload_page),

]

