from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import JsonResponse
from pymongo import MongoClient
from django.conf import settings
import json
import random
from django.utils.html import format_html

def send_otp(email):
    
    if email:
        
        otp = random.randint(100000, 999999)
        client = MongoClient("mongodb://localhost:27017/")  # Adjust if using a different host/port
        db = client['otp_session']
        collection = db['otp_verify']
        collection.insert_one({
            'otp': otp,
            'email': email
        })
        verify = otp
        subject = "Your OTP Code"
        message = format_html(
    '<p style="font-size:16px;"><strong>🔑 Your OTP for email verification is:</strong></p>'
    '<h2 style="color:#1a73e8; font-size:24px;">{}</h2>'
    '<p style="font-size:14px; color:#555;">Do not share this code with anyone.</p>', otp
)

        send_mail(
    subject,
    "",  # Empty because we are using the HTML version
    "udiman03@gmail.com",
    [email],
    fail_silently=False,
    html_message=message,  # Include HTML content
)
          

            
           

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']  # Capture the selected role
        settings.global_email=email
        # MongoDB connection
        client = MongoClient("mongodb://localhost:27017/")  # Adjust if using a different host/port
        
        if role == 'candidate':
            # Connect to candidate database and collection
            db = client['user']
            collection = db['personal']

            # Check if username already exists
            if collection.find_one({'username':username,'email':email}):
                return render(request, 'signup.html',{'email':email,'username': username,'password':password,'role':role,'ispresent':True})
                # request.session['error_message'] = "Username already exists! Please login."
                # return redirect('login')
                
            send_otp(email)
            # Insert candidate data
            collection.insert_one({
                'email': email,
                'username': username,
                'password': password,
                'role': 'candidate',
            })
            return redirect('verify_otp')  # Redirect to login page after signup

            # request.session['success_message'] = "Candidate account created successfully!"
        
        elif role == 'recruiter':
            # Connect to recruiter database and collection
            db = client['recruiter_db']
            collection = db['recruiter']

            # Check if username already exists
            if collection.find_one({'username':username,'email':email}):
                # request.session['error_message'] = "Username already exists! Please login."
                # return redirect('login')
                return render(request, 'signup.html',{'email':email,'username': username,'password':password,'role':role,'ispresent':True})
            send_otp(email)

            # Insert recruiter data
            collection.insert_one({
                'email': email,
                'username': username,
                'password': password,
                'role': 'recruiter',
            })
            return redirect('verify_otp')  # Redirect to login page after signup

            # request.session['success_message'] = "Recruiter account created successfully!"

    return render(request, 'signup.html')

def loginpag(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        settings.global_email=email
        # MongoDB connection
        client = MongoClient("mongodb://localhost:27017/")  # Adjust if using a different host/port
        
        # Check in Candidate Database
        user_db = client['user']
        candidate_collection = user_db['personal']
        candidate = candidate_collection.find_one({'email': email, 'password': password})

        if candidate:
            # request.session['success_message'] = f"Welcome, {candidate['username']}!"
            return redirect('user:user_dashboard')

        # Check in Recruiter Database
        recruiter_db = client['recruiter_db']
        recruiter_collection = recruiter_db['recruiter']
        recruiter = recruiter_collection.find_one({'email': email, 'password': password})

        if recruiter:
            # request.session['success_message'] = f"Welcome, {recruiter['username']}!"
            return redirect('recruiter:recruiter_dashboard')

        # No match found
        # request.session['error_message'] = "Invalid username or password!"
        return redirect('login')  # Redirect back to login page

    # Retrieve and clear session messages
    # success_message = request.session.pop('success_message', None)
    # error_message = request.session.pop('error_message', None)

    return render(request, 'login.html')

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
    #     session_otp = request.session.get('otp')
        client = MongoClient("mongodb://localhost:27017/")  # Adjust if using a different host/port
        db = client['otp_session']
        collection = db['otp_verify']
        data = collection.find_one({'email': settings.global_email},sort=[("_id", -1)])
        if int(data['otp']) == int(otp):
    #         request.session.pop('otp', None)  # Clear the OTP after verification
    #         request.session['success_message'] = "OTP verified successfully!"
            return redirect('login')
        else:
            return redirect('verify_otp')

    return render(request, 'verify_otp.html')

def adminlogin(request):
    if request.method=='POST':
        email = request.POST['email']
        password = request.POST['password'] 
        settings.global_email=email
        client = MongoClient("mongodb://localhost:27017/")
        admin_db = client['Admin_db']
        admin_collection=admin_db['Admin_login_details']
        candidate = admin_collection.find_one({'email': email, 'password': password})
        if candidate:
            return redirect('admindashboard')
        return redirect('adminlogin')
    return render(request,'Admin_portal_login.html')

def admindashboard(request):
    return render(request,'Admin_dashboard.html')
def candidate_details(request):
    return render(request,'Admin_user_table.html')