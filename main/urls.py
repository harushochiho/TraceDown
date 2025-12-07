from django.urls import path
from main import views

urlpatterns = [
    path('', views.create_item, name='create_item'),
    path('submit_item/', views.submit_item, name='submit_item'),
]