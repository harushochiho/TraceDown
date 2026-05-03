from django.urls import path
from main import views

urlpatterns = [
    path('', views.create_item, name='create_item'),
    path('submit_item/', views.submit_item, name='submit_item'),
    path('records/', views.retrieval, name='retrieval'),
    path('update_item/<int:item_id>/', views.update_item, name='update_item'),
    path('records/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('image_upload/', views.image_upload, name='image_upload'),
    path('image_recognition_req/', views.image_recognition_req, name='image_recognition_req'),
]
