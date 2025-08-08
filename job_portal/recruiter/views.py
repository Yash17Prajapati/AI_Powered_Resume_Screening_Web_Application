from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
from bson.objectid import ObjectId
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, FileResponse, HttpResponse, JsonResponse
import gridfs
import pdfminer.high_level
import nltk
import string
import numpy as np
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from threading import Thread

client = MongoClient("mongodb://localhost:27017/")
db = client["recruiter_db"]
job_collection = db["post_job"]
resume_collection = db["recruiter_resume_details"]
db1 = client["AI_screening_db"]
ai_result_collection = db1["AI_screening_result"]

nltk.download('stopwords')
fs = gridfs.GridFS(db)

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    return " ".join([word for word in words if word not in stop_words])

def extract_text_from_pdf(file_id):
    file = fs.get(file_id)
    return pdfminer.high_level.extract_text(file)

def ai_screening(job_id):
    print(f"[ai_screening] Thread started for job_id: {job_id}")
    try:
        job = job_collection.find_one({"_id": ObjectId(job_id)})
        if not job:
            print("[ai_screening] Job not found in DB.")
            return

        job_text = f"{job.get('Job_description', '')} {job.get('Skill_required', '')} {job.get('Education_qualify', '')}"
        job_text = preprocess_text(job_text)

        resumes = list(resume_collection.find({"job_apply_id": ObjectId(job_id)}))

        high_match = []
        medium_match = []
        low_match = []

        for candidate in resumes:
            try:
                resume_id = candidate["resume_details"]
                resume_text_raw = extract_text_from_pdf(resume_id)
                resume_text = preprocess_text(resume_text_raw)

                if not job_text.strip() or not resume_text.strip():
                    continue

                vectorizer = TfidfVectorizer()
                tfidf_matrix = vectorizer.fit_transform([job_text, resume_text])
                score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
                score_rounded = round(score, 2)

                result_data = {
                    "email": candidate["email"],
                    "score": score_rounded,
                    "resume_id": resume_id
                }

                if score >= 0.65:
                    high_match.append(result_data)
                elif 0.3 <= score < 0.65:
                    medium_match.append(result_data)
                elif 0.1 <= score < 0.3:
                    low_match.append(result_data)

            except Exception as e:
                print(f"[ai_screening] Error processing resume for {candidate.get('email')}: {str(e)}")

        ai_result_collection.insert_one({
            "job_id": ObjectId(job_id),
            "high_match": high_match,
            "medium_match": medium_match,
            "low_match": low_match
        })

        job_collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"re_evaluation_required": False}}
        )

    except Exception as e:
        print(f"[ai_screening] ERROR: {str(e)}")

def start_ai_screening(request, job_id):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        job = job_collection.find_one({"_id": ObjectId(job_id)})
        if not job:
            return JsonResponse({"error": "Job not found"}, status=404)

        # Default to True if field doesn't exist
        if not job.get("re_evaluation_required", True):
            return JsonResponse({"error": "Re-evaluation not required"}, status=400)

        thread = Thread(target=ai_screening, args=(job_id,))
        thread.start()
        return JsonResponse({"message": f"AI Screening started for Job ID {job_id}"})
    return JsonResponse({"error": "Invalid Request"}, status=400)

def get_ai_results(request, job_id):
    latest_doc = ai_result_collection.find_one(
    {"job_id": ObjectId(job_id)},
    sort=[('_id', -1)]
)
    print(latest_doc)
    # result = ai_result_collection.find_one({"job_id": ObjectId(job_id)})
    if latest_doc:
        latest_doc['job_id'] = str(latest_doc['job_id'])
        for level in ['high_match', 'medium_match', 'low_match']:
            for candidate in latest_doc.get(level, []):
                candidate['resume_id'] = str(candidate['resume_id'])

        return render(request, 'recruiter/AI_shortlisted_candidate_table.html', {'results': [latest_doc]})
    return JsonResponse({"status": "error", "message": "No AI results found"})
def recruiter_dashboard(request):
    """
    Displays a dashboard of all jobs posted by the current recruiter.
    """
    # jobs = Job.objects.filter(posted_by=request.user)  # Get jobs posted by the logged-in recruiter
    # return render(request, 'recruiter/dashboard.html', {'jobs': jobs})  # Uses common template for recruiter dashboard
    return render(request,'recruiter/dashboard.html')

# @login_required
def post_job(request):
    """
    Allows a recruiter to post a new job.
    """
    
    client = MongoClient("mongodb://localhost:27017/")
    db1=client['user']
    db = client['recruiter_db']
    collection = db['post_job']
    collection1=db1['personal']
    if request.method == 'POST':
        job_title=request.POST['job_title']
        job_desc=request.POST['job_description']
        comp_name=request.POST['company_name']
        job_loc=request.POST['job_location']
        emp_type=request.POST['employment_type']
        exp_lvl=request.POST['experience_level']
        salary_rng=request.POST['salary_range']
        skll_req=request.POST['skills_required']
        edu_qualify=request.POST['education']
        app_deadline=request.POST['application_deadline']
        job_cate=request.POST['job_category']
        vacan=request.POST['vacancies']
        contact_info=request.POST['contact_info']
        post_email=settings.global_email
        post_date=datetime.now().strftime('%B %d, %Y')
        collection.insert_one({
                'Job_title':job_title,
                'Job_description':job_desc,
                'Company_name':comp_name,
                'Job_location':job_loc,
                'Employment_type':emp_type,
                'Experience_level':exp_lvl,
                'Salary_range':salary_rng,
                'Skill_required':skll_req,
                'Education_qualify':edu_qualify,
                'Application_deadline':app_deadline,
                'Job_category':job_cate,
                'Vacancy':vacan,
                'Contact_info':contact_info,
                'Posted_via_email':post_email,
                'Job_post_date':post_date
            })
        emails = collection1.find({}, {'email': 1, '_id': 0})

# Loop through the result and print emails
        email_list = [email['email'] for email in emails]

# Output the email list
# print(email_list)
#         send_mail(
#     'New Job Posting',
#     f'Dear candidate,\n\nA new job has been posted.\nJob-Title: {job_title}.\nJob-Company: {comp_name}.\nType: {emp_type}.\nExperience-Level: {exp_lvl}.\nSalary-Range: {salary_rng}.\nJob Vacancy: {vacan}.\nJob Category: {job_cate}',
#     'udiman03@gmail.com',  # Sender email
#     email_list,  # Recipient email
#     fail_silently=False,
# )
        return redirect('recruiter:job_posted')
    # if request.method == 'POST':
    #     # Handle job posting submission
    #     Job.objects.create(
    #         title=request.POST['title'],
    #         description=request.POST['description'],
    #         location=request.POST['location'],
    #         salary=request.POST['salary'],
    #         company_name=request.POST['company_name'],
    #         posted_by=request.user,  # Link the job to the logged-in recruiter
    #     )
    #     return redirect('recruiter_dashboard')  # Redirect to the recruiter dashboard after posting the job
    
    # Render job posting form for GET request
    return render(request, 'recruiter/post_job.html')  # Uses common template for posting job
def job_posted(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection = db['post_job']
    page = int(request.GET.get('page', 1))  # Get page number from query params
    per_page = 4
    result=list(collection.find({'Posted_via_email':settings.global_email}))
    total_jobs=len(result)
    jobs_cursor = collection.find({'Posted_via_email':settings.global_email}).skip((page - 1) * per_page).limit(per_page)
    result1=[]
    for job in jobs_cursor:
        job['id'] = str(job.pop('_id'))
        result1.append(job)
    # print(result)
    total_pages = (total_jobs + per_page - 1) // per_page
    return render(request,'recruiter/past-jobs.html',{'jobs':result1,'page': page,
        'total_pages': total_pages})
# @login_required
def view_applicants(request, job_id):
    """
    Displays a list of applicants for a particular job.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    db1=client['user']
    collection1=db1['personal']
    collection = db['recruiter_resume_details']
    req_jobs=collection.find({'job_apply_id':ObjectId(job_id)})
    print(req_jobs)
    results=[]
    for req_job in req_jobs:
        print(req_job)
        user_info = collection1.find_one({'email': req_job['email']})
        
        results.append({
            'user_name': user_info['username'] if user_info else "Unknown",
            'user_email': req_job['email'],
            'Applied_on': req_job['Date'],
            'Additional_job_applications': collection.count_documents({'email': req_job['email']}) - 1,
            'Document_uploaded': ObjectId(req_job['resume_details']),  # Assuming route to fetch resume
            'job_id': job_id
        })
        print(results)
        print(len(results))
    return render(request,'recruiter/view_applicants.html',{'results':results,'count':len(results)})
def view_job(request,job_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection = db['post_job']
    job = collection.find_one({"_id": ObjectId(job_id)})
    return render(request,'recruiter/view_details.html',{'job_data':job})
def edit_job_post(request,job_id):
    employment_types = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance']
    experience_levels = ['Entry-level', 'Mid-level', 'Senior-level', 'Executive']
    job_categories = ['IT', 'Finance', 'Healthcare', 'Education', 'Others']
    job = job_collection.find_one({"_id": ObjectId(job_id)})

    if request.method == 'POST':
        updated_data = {
            'Job_title': request.POST['job_title'],
            'Job_description': request.POST['job_description'],
            'Company_name': request.POST['company_name'],
            'Job_location': request.POST['job_location'],
            'Employment_type': request.POST['employment_type'],
            'Experience_level': request.POST['experience_level'],
            'Salary_range': request.POST['salary_range'],
            'Skill_required': request.POST['skills_required'],
            'Education_qualify': request.POST['education'],
            'Application_deadline': request.POST['application_deadline'],
            'Job_category': request.POST['job_category'],
            'Vacancy': request.POST['vacancies'],
            'Contact_info': request.POST['contact_info'],
            'Last_edited': datetime.now(),
            're_evaluation_required': True
        }
        job_collection.update_one({"_id": ObjectId(job_id)}, {"$set": updated_data})
        return redirect('recruiter:job_posted')

    return render(request, 'recruiter/edit_page.html', {
        'job_data': job,
        'employment_types': employment_types,
        'experience_levels': experience_levels,
        'job_categories': job_categories
    })
def delete_post(request,job_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection = db['post_job']
    try:
        job_object_id = ObjectId(job_id)
    except Exception as e:
        return redirect('recruiter:job_posted')  # If ObjectId is invalid, redirect
    
    # Delete the job post using ObjectId
    collection.delete_one({"_id": job_object_id})

    # Redirect to the job posted page (after successful deletion)
    return redirect('recruiter:job_posted')

def result_jobs(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection = db['post_job']

    current_date_str = datetime.now().strftime("%Y-%m-%d")

    # Get jobs posted by the recruiter with deadline passed
    req_jobs = collection.find({
        'Posted_via_email': settings.global_email,
        'Application_deadline': {"$lte": current_date_str}
    })

    results = []
    for req_job in req_jobs:
        results.append({
            'job_id': req_job['_id'],
            'Application_deadline': req_job['Application_deadline'],
            'job_openings': req_job.get('Vacancy', '-'),
            're_evaluation_required': req_job.get('re_evaluation_required', False)  # ✅ INCLUDE THIS
        })

    return render(request, 'recruiter/Result.html', {'results': results})


def doc_details(request, job_id, doc_id):
    """
    Fetches and serves a resume document stored in GridFS.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    fs = gridfs.GridFS(db)

    # ✅ Ensure job_id & doc_id are valid ObjectIds
    if not ObjectId.is_valid(job_id) or not ObjectId.is_valid(doc_id):
        return HttpResponse("Invalid job or document ID", status=400)

    collection1 = db['recruiter_resume_details']
    application = collection1.find_one({
        'job_apply_id': ObjectId(job_id),
        'resume_details': ObjectId(doc_id)  # Ensure it matches GridFS file ID
    })

    # ✅ Handle missing application or missing resume
    if not application or 'resume_details' not in application:
        return HttpResponse("Resume not found", status=404)

    file_id = application['resume_details']

    try:
        # ✅ Retrieve the file from GridFS
        file_data = fs.get(file_id)

        # ✅ Handle missing filename
        filename = file_data.filename if hasattr(file_data, "filename") else "resume.pdf"

        # ✅ Serve the file as a response
        response = FileResponse(file_data, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response

    except gridfs.errors.NoFile:
        return HttpResponse("File not found in GridFS", status=404)
    
def recruiter_view_job(request,job_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recruiter_db']
    collection=db['post_job']
    job_details=collection.find_one({'_id':ObjectId(job_id)})
    return render(request,'recruiter/job_detail_popup.html',{'job_data':job_details})
