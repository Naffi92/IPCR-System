from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    
    # Template Builder
    path('templates/', views.template_dashboard, name='template_dashboard'),
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/<int:template_id>/', views.template_detail, name='template_detail'),
    
    # Categories
    path('templates/<int:template_id>/add-category/', views.add_category, name='add_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    
    # Goals
    path('categories/<int:category_id>/add-goal/', views.add_goal, name='add_goal'),
    path('goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    
    # KRAs
    path('goals/<int:goal_id>/add-kra/', views.add_kra, name='add_kra'),
    path('kras/<int:kra_id>/delete/', views.delete_kra, name='delete_kra'),
    
    # Columns
    path('templates/<int:template_id>/add-column/', views.add_column, name='add_column'),
    path('columns/<int:column_id>/delete/', views.delete_column, name='delete_column'),
]