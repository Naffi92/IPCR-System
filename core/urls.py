from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Ratee URLs
    path('my-ipcr/', views.my_ipcr, name='my_ipcr'),
    path('my-ipcr/add-target/', views.add_target, name='add_target'),
    path('my-ipcr/edit-target/<int:target_id>/', views.edit_target, name='edit_target'),
    path('my-ipcr/delete-target/<int:target_id>/', views.delete_target, name='delete_target'),
]