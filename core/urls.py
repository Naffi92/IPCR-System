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

    # Ratee Submit
    path('my-ipcr/submit/', views.submit_ipcr, name='submit_ipcr'),
    
    # Rater URLs
    path('supervisor/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor/review/<int:ipcr_id>/', views.review_ipcr, name='review_ipcr'),

    path('supervisor/appraise/<int:ipcr_id>/', views.appraise_ipcr, name='appraise_ipcr'),
]