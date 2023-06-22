from django.urls import path

from . import views

app_name = "openai_example"

urlpatterns = [
    path("", views.home, name="openai_home"),
    path("images/", views.image_demo, name="image_demo"),
    path('upload_file', views.upload_file, name='upload_file'),
    path('create_first_mode_checkout_session', views.create_first_mode_checkout_session, name='create_first_mode_checkout_session'),
    path('create_second_mode_checkout_session', views.create_second_mode_checkout_session, name='create_second_mode_checkout_session'),
    path('check_payed_status', views.check_payed_status, name='check_payed_status')
]
