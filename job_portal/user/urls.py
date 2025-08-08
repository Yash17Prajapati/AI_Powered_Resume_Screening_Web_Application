from django.urls import path
from . import views
# from .views import doc_details
app_name='user'
urlpatterns = [
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('jobs/', views.job_list, name='job_list'),
    path('applied/', views.applied, name='applied'),
    path('job/<str:job_id>/detail/',views.view_details,name='view_details'),
    path('apply/<str:job_id>/',views.apply_job,name='apply_job'),
    path('application/<str:job_id>/doc_details/<str:doc_id>/',views.doc_details,name='document_details'),
    path('With-Draw-Application/<str:job_id>/',views.withdraw,name='withdraw'),
    path('Checking-Application-Status/<str:job_id>/',views.applicationStatus,name='application_Status')
]
