from django.urls import path
from . import views

app_name = 'learners'

urlpatterns = [
    path('', views.LearnerListView.as_view(), name='list'),
    path('<int:pk>/', views.LearnerDetailView.as_view(), name='detail'),
    path('create/', views.LearnerCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.LearnerUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.LearnerDeleteView.as_view(), name='delete'),
    path('<int:pk>/file/<str:field_name>/', views.LearnerFileView.as_view(), name='file'),
    path('import/', views.ImportLearnersView.as_view(), name='import'),
    path('export/', views.ExportLearnersView.as_view(), name='export'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('users/', views.UserManagementView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('<int:learner_id>/evaluations/create/', views.evaluation_create, name='evaluation_create'),
    path('evaluations/<int:pk>/update/', views.EvaluationUpdateView.as_view(), name='evaluation_update'),
    path('evaluations/<int:pk>/delete/', views.EvaluationDeleteView.as_view(), name='evaluation_delete'),
    path('evaluations/', views.EvaluationListView.as_view(), name='evaluation_list'),
    path('evaluations/create/', views.EvaluationCreateSelectView.as_view(), name='evaluation_create_select'),
    path('<int:pk>/social-history/update/', views.SocialHistoryUpdateView.as_view(), name='social_history_update'),
    path('<int:pk>/social-history/create/', views.SocialHistoryCreateView.as_view(), name='social_history_create'),
] 