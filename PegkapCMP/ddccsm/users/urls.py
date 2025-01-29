from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListView.as_view(), name='list'),
    path('create/', views.UserCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.UserDeleteView.as_view(), name='delete'),
    path('<int:pk>/reset-password/', views.UserPasswordResetView.as_view(), name='reset_password'),
    path('management/', views.ManagementDashboardView.as_view(), name='management_dashboard'),
    path('activity/', views.UserActivityView.as_view(), name='activity'),
    path('activity/export/', views.ExportUserActivityView.as_view(), name='export_activity'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
] 