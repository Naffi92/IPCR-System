from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    
    # Template Builder URLs
    path('templates/', views.template_dashboard, name='template_dashboard'),
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/<int:template_id>/', views.template_detail, name='template_detail'),
    path('templates/<int:template_id>/add-category/', views.add_category, name='add_category'),
    path('templates/<int:template_id>/add-column/', views.add_column, name='add_column'),
    path('categories/<int:category_id>/add-kra/', views.add_kra, name='add_kra'),
]