from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . views import  certificate_list

from .views import reset_password_in_login

urlpatterns = [

    path('', views.home, name='home'),

    path('admin-login/', views.admin_login, name='admin_login'),
    path('user-login/', views.user_login, name='user_login'),
   
    path('password-reset-requests/', views.manage_password_reset_requests, name='manage_password_reset_requests'),
    path('password-reset-requests/create/',views. create_password_reset_request, name='create_password_reset_request'),
    path('password-reset-requests/edit/<int:pk>/',views. edit_password_reset_request, name='edit_password_reset_request'),
    path('password-reset-requests/delete/<int:pk>/', views.delete_password_reset_request, name='delete_password_reset_request'),
    
    path('admin-notifications/',views. admin_notifications, name='admin_notifications'),
    path('admin-notifications/',views. manage_admin_notifications, name='manage_admin_notifications'),
    path('admin-notifications/create/',views. create_admin_notification, name='create_admin_notification'),
    path('admin-notifications/edit/<int:pk>/', views.edit_admin_notification, name='edit_admin_notification'),
    path('admin-notifications/delete/<int:pk>/', views.delete_admin_notification, name='delete_admin_notification'),
    # Authentication routes
    path('login/', views.login_view, name='login'),
    path('reset_password/', views.reset_password_view, name='reset_password'), 
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    path('reset-password-in-login/<int:user_id>/', reset_password_in_login, name='reset_password_in_login'),
    # Password reset routes
    path('forgot-password/', views.forgot_password_request, name='forgot_password'),
    path('reset-password/', views.user_reset_password, name='reset_password'),

    # Home after login
    path('home/', views.homeDisplay, name='home'),
    path('home2/', views.homeDisplay, name='home2'),

    # Admin-specific routes (for admin to manage password resets)
    path('admin-remove-password/<int:user_id>/', views.admin_remove_password, name='admin_remove_password'),

    path('batches/', views.batchmaster_list, name='batchmaster_list'),
    path('batches/create/', views.batchmaster_create, name='batchmaster_create'),
    path('batches/update/<int:pk>/', views.batchmaster_update, name='batchmaster_update'),
    path('batches/delete/<int:pk>/', views.batchmaster_delete, name='batchmaster_delete'),
    path('batches/search/', views.batchmaster_search, name='batchmaster_search'),
    path('batches/report/',views. batchmaster_report, name='batchmaster_report'), 

    path('semesters/', views.semester_list, name='semester_list'),
    path('semesters/create/', views.semester_create, name='semester_create'),
    path('semesters/update/<int:pk>/',views. semester_update, name='semester_update'),
    path('semesters/delete/<int:pk>/',views. semester_delete, name='semester_delete'),
    path('semesters/search/', views.semester_search, name='semester_search'),
    
    path('semester/report/', views.semester_report, name='semester_report'),  # For all semesters
    path('semester/report/<int:pk>/',views. semester_report, name='semester_report_specific'),  # For specific semester

    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/search/', views.student_search, name='student_search'),

    path('students/report/', views.student_report, name='student_report_all'),
    path('students/report/<int:pk>/', views.student_report, name='student_report'),

    path('certificates/', views.certificate_list, name='certificate_list'),
    path('certificates/create/', views.certificate_create, name='certificate_create'),
    path('certificates/<int:pk>/update/', views.certificate_update, name='certificate_update'),
    path('certificates/<int:pk>/delete/', views.certificate_delete, name='certificate_delete'),
    path('certificates/search/', views.certificate_search, name='certificate_search'),
    path('certificates/report/', views.certificate_report, name='certificate_report'),

    path('backup/', views.backup_data, name='backup_data'),
    path('restore/', views.restore_data, name='restore_data'),
    path('restore/', views.restore_data, name='backup_restore'),


    path('transactions/list', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/update/<int:pk>/', views.transaction_update, name='transaction_update'),
    path('transactions/delete/<int:pk>/', views.transaction_delete, name='transaction_delete'),
    path('transactions/report/', views.transaction_report, name='transaction_report'),
    ]
