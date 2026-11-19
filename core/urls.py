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

    # Rating Periods
    path('rating-periods/', views.rating_period_dashboard, name='rating_period_dashboard'),
    path('rating-periods/create/', views.create_rating_period, name='create_rating_period'),

    # Position Matrix
    path('templates/<int:template_id>/matrix/', views.position_matrix, name='position_matrix'),

    path('my-ipcr/', views.my_ipcr, name='my_ipcr'),

    path('rating-periods/<int:period_id>/edit/', views.edit_rating_period, name='edit_rating_period'),
    path('rating-periods/<int:period_id>/delete/', views.delete_rating_period, name='delete_rating_period'),

    path('templates/<int:template_id>/edit/', views.edit_template, name='edit_template'),
    path('templates/<int:template_id>/delete/', views.delete_template, name='delete_template'),

    path('my-ipcr/add-row/', views.add_ipcr_row, name='add_ipcr_row'),
]