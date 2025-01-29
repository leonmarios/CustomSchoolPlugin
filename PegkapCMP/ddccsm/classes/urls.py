from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.ClassListView.as_view(), name='list'),
    path('create/', views.ClassCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ClassDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ClassUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ClassDeleteView.as_view(), name='delete'),
    path('teacher-assignments/', views.TeacherAssignmentListView.as_view(), name='teacher_assignment_list'),
    path('teacher-assignments/create/', views.TeacherAssignmentCreateView.as_view(), name='teacher_assignment_create'),
    path('teacher-assignments/<int:pk>/update/', views.TeacherAssignmentUpdateView.as_view(), name='teacher_assignment_update'),
    path('teacher-assignments/<int:pk>/delete/', views.TeacherAssignmentDeleteView.as_view(), name='teacher_assignment_delete'),
] 