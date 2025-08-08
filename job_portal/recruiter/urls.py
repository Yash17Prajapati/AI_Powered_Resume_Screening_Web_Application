from django.urls import path
from . import views
app_name='recruiter'
urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('post-job/', views.post_job, name='post_job'),
    path('job-posted/',views.job_posted,name='job_posted'),
    path('job/<str:job_id>/detail', views.view_job, name='view_job'),
    # path('jobs/<str:job_id>/apply/', views.apply_job, name='apply_job'),
    path('view-applicants/<str:job_id>/', views.view_applicants, name='view_applicants'),
    path('edit-job-post/<str:job_id>/',views.edit_job_post,name='edit_job_post'),
    path('delete/<str:job_id>/',views.delete_post,name='delete_post'),
    path('view-result/Posted_jobs/',views.result_jobs,name='result_jobs'),
    path('application/<str:job_id>/doc_details/<str:doc_id>/',views.doc_details,name='document_details'),
    path('ai_screening/start/<str:job_id>/', views.start_ai_screening, name='start_ai_screening'),
    path('ai_screening/result/<str:job_id>/', views.get_ai_results, name='get_ai_results'),
    path('recruiter/view-job/<str:job_id>/',views.recruiter_view_job,name='recruiter_view_job')
]
