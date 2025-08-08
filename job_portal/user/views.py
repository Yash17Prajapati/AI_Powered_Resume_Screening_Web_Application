from django.shortcuts import render, redirect
# from .models import Job, Application
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime,date
from django.http import HttpResponseRedirect,FileResponse,HttpResponse
from bson.objectid import ObjectId
import gspread
import gridfs
import re
import time
# from user.models import Job, Application

# Ensure the user is logged in and a recruiter
# @login_required
def job_list(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection = db['post_job']
    collection1=db['recruiter_resume_details']
    search_term = request.GET.get('search', '').strip()
    page = int(request.GET.get('page', 1))  # Get page number from query params
    per_page = 4  # Number of jobs per page
    # Build the filter query based on the provided search term
    filter_query = {}
    if search_term:
        search_terms = re.split(r'[, ]+', search_term)  
        search_terms = [term.strip() for term in search_terms if term.strip()]
        regex_patterns = [re.compile(term, re.IGNORECASE) for term in search_terms]
        # Search in company name, job location, and skills required fields
        filter_query['$or'] = [
            {'Company_name': {'$in': regex_patterns}},  # Match company name
            {'Job_location': {'$in': regex_patterns}},  # Match job location
            {'Skills_required': {'$in': regex_patterns}},  # Match skills
            {'Employment_type': {'$in': regex_patterns}},  # Match employment type
            {'Experience_level': {'$in': regex_patterns}},  # Match experience level
        ]
        for term in search_terms:
            if term.isdigit():
                filter_query['$or'].append({'Salary': int(term)})
    currentdate=datetime.now()
    total_jobs = collection.count_documents(filter_query)
    
    # Apply pagination using skip and limit
    jobs_cursor = collection.find(filter_query).skip((page - 1) * per_page).limit(per_page)
    
    # Fetch filtered job posts from MongoDB
    # result = list(collection.find(filter_query))
    result=[]
    # tokenvalid=False
    for job in jobs_cursor:
        job['id'] = str(job.pop('_id'))
        job['deadline_exceeded'] = datetime.strptime(job['Application_deadline'], '%Y-%m-%d') < currentdate
        count_applicants = collection1.count_documents({'job_apply_id': ObjectId(job['id'])})
        applied_found=collection1.find_one({'job_apply_id':ObjectId(job['id']),'email':settings.global_email})
        if applied_found:
            job['applied_detail']=True 
        if count_applicants:
            job['count']=count_applicants
        result.append(job)
    total_pages = (total_jobs + per_page - 1) // per_page
    print(result)
    return render(request, 'user/job_list.html', {'jobs': result,'page': page,
        'total_pages': total_pages,
        'search_term': search_term})
    # jobs = Job.objects.all()
    # return render(request, 'user/job_list.html', {'jobs': jobs})
    # return render(request,'user/job_list.html')

def applied(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection = db['post_job']
    collection1=db['recruiter_resume_details']
    page = int(request.GET.get('page', 1))  # Get page number from query params
    per_page = 4
    
    job_applied_details=list(collection1.find({'email':settings.global_email}))
    total_jobs=len(job_applied_details)
    jobs_cursor = collection1.find({'email':settings.global_email}).skip((page - 1) * per_page).limit(per_page)
    result=[]
    for job_applied_detail in jobs_cursor:
        job_detail=collection.find_one({'_id':job_applied_detail['job_apply_id']})
        job_applied_detail['job_detail']=job_detail
        result.append(job_applied_detail)

    total_pages = (total_jobs + per_page - 1) // per_page    
    print(job_applied_details) 
    return render(request,'user/applied.html',{'jobs':result,'page': page,
        'total_pages': total_pages})

def user_dashboard(request):
    return render(request,'user/dashboard.html')

def view_details(request,job_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection = db['post_job']
    job = collection.find_one({"_id": ObjectId(job_id)})
    return render(request,'user/view_details.html',{'job_data':job})
def apply_job(request,job_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection = db['post_job']
    job = collection.find_one({"_id": ObjectId(job_id)})
    collection1 = db['recruiter_resume_details']
    fs = gridfs.GridFS(db)  # Using GridFS for storing large files like resumes

    # Check if job application already exists
    job_apply_details = collection1.find_one({'job_apply_id': ObjectId(job_id),'email':settings.global_email})
    
    # If the user has already applied, show the application submitted message
    if job_apply_details:
        return render(request, 'user/applyform.html', {'job_apply_id': job_id, 'job_apply_details': job_apply_details})

    resume = None
    if request.method == 'POST':
        # Handling the file upload using GridFS
        resume = request.FILES.get('file')
        if resume:
            file_id = fs.put(resume.read(), filename=resume.name, contentType="application/pdf")
            # Insert application details into the collection
            collection1.insert_one({
                'resume_details': file_id,  # Store the file ID
                'job_apply_id': ObjectId(job_id),
                'email': settings.global_email,
                'recruiter_posted_email': job['Posted_via_email'],
                'Date':date.today().strftime("%Y-%m-%d")
            })
        time.sleep(3)
        return redirect(request.path)

    return render(request, 'user/applyform.html', {'job_apply_id': job_id})
def view_app_profile(request):
    return render(request,'user/user_application_profile.html')
def doc_details(request,job_id,doc_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    fs = gridfs.GridFS(db)

    # Retrieve application details (get the file ID)
    collection1 = db['recruiter_resume_details']
    application = collection1.find_one({
    'job_apply_id': ObjectId(job_id),
    'email': settings.global_email,
    'resume_details': ObjectId(doc_id)  # Ensure doc_id is an ObjectId
})
    if not application or 'resume_details' not in application:
        return HttpResponse("Resume not found", status=404)

    file_id = application['resume_details']

    # Retrieve the file from GridFS
    file_data = fs.get(file_id)

    # Serve the file as a response
    response = FileResponse(file_data, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{file_data.filename}"'
    return response
    return render(request,'user/documentpage.html')
def withdraw(request,job_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection=db['recruiter_resume_details']
    try:
        job_object_id = ObjectId(job_id)
    except Exception as e:
        return redirect('user:applied')
    collection.delete_one({"job_apply_id": job_object_id,'email':settings.global_email})
    return redirect('user:applied')
def applicationStatus(request,job_id):
    return render(request,'user/check_application_status.html')