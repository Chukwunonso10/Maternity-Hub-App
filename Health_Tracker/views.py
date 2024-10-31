from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from .models import UserSymptoms, AnalysisResults
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import UserSymptoms, AnalysisResults, DailyCheckup, CustomUser, Notification
from django.db import IntegrityError
from openai.error import RateLimitError
from datetime import timedelta
import openai
import time


# Create your views here.
def UserRegistration(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the user
            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, "UserRegistration.html", {"form": form})

@login_required
def Analysis(request,symptom_id):
    symptom = get_object_or_404(UserSymptoms, id=symptom_id, user=request.user)
    analysis = AnalysisResults.objects.filter(user_symptom=symptom).first()  # Get analysis results

    return render(request, 'Analysis.html', {'symptom': symptom, 'analysis': analysis})
@login_required
def CheckUp(request):
    if request.method == "POST":
        checkup_data = request.POST.get("checkup_data")
        suggestions = request.POST.get("suggestions")
        DailyCheckup.objects.create(user=request.user, checkup_date=datetime.date.today(), checkup_data=checkup_data, suggestions=suggestions)
        messages.success(request, "Daily checkup recorded successfully.")
        return redirect("CheckUp")  # Redirect to checkup page
    return render(request, "CheckUp.html")  # Render form to add daily checkup

@login_required
def symptoms(request):
    if request.method == "POST":
        symptom_text = request.POST.get("symptoms")  # Match field name
        severity = request.POST.get("severity")
        print(f"Symptom: {symptom_text}, Severity: {severity}") 

        if symptom_text and severity:  # Ensure inputs are not empty
            user_symptoms = UserSymptoms.objects.create(user=request.user, symptoms=symptom_text, symptoms_severity=severity)
            messages.success(request, f"Symptom '{symptom_text}' recorded successfully with severity {severity}.")
            return redirect("analyze_symptoms", symptom_id=user_symptoms.id)  # Redirect back to symptoms page
        
        else:
            messages.error(request, "Please provide both symptom and severity.")
            return redirect('symptoms')

    return render(request, 'Symptoms.html')


def login_view(request):
    print("Login view accessed")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(f"Attempting login with Username: {username}, Password: {password}")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("Login successful")

            return redirect("dashboard")  # or any other route you wish to redirect to
        else:
            messages.error(request,"Invalid username or Password.")
            return render(request, "login.html")
    return render(request, "login.html")  # render the login form

def logout_view(request):
    logout(request)
    return redirect("login")  # Redirect to login after logging out

@login_required
def dashboard_view(request):
    user = request.user  # Accessing the current logged-in user
    
    # Retrieve the 5 most recent symptom analyses for the logged-in user
    recent_symptoms = (
        UserSymptoms.objects.filter(user=user)
        .select_related('analysisresults')  # Ensure related AnalysisResults are pre-fetched
        .order_by('-created_at')[:5]
    )

    # Access LMP date directly from the user model, if it exists on the CustomUser model
    edd = calculate_edd(user.lmp_date) if hasattr(user, 'lmp_date') and user.lmp_date else None

    # Retrieve unread notifications for the user
    user_notifications = Notification.objects.filter(user=user, read=False)

    # Prepare context data to be passed to the template
    context = {
        'user': user,
        'recent_symptoms': recent_symptoms,
        'edd': edd,
        'user_notifications': user_notifications,
    }

    return render(request, 'dashboard.html', context)

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user, read=False)
    return render(request, 'notifications.html', {'notifications': user_notifications})
@login_required
def about_us(request):
    return render(request, 'about_us.html')


# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

def get_ai_recommendation(symptoms_text):
    prompt = f"As a medical assistant, provide health recommendations for a pregnant mother experiencing the following symptoms: {symptoms_text}. Please consider safety for both the mother and the unborn child."
    recommendations = "No recommendation available at the moment."
    
    try:
        # API request to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",  # Update if using a different model
            messages=[{"role": "user", "content": f"Based on these symptoms: {symptoms_text}, what are your recommendations?"}],
            max_tokens=100,
        )
        
        # Extract recommendation from the response
        recommendations = response['choices'][0]['message']['content']

    except openai.error.RateLimitError:
        print('Rate limit exceeded. Retrying after 60 seconds...')
        time.sleep(20)
        
    except Exception as e:
        print(f"API call failed: {e}")

    # Return or save recommendations with a default value to avoid None
    return recommendations

@login_required
def analyze_symptoms(request, symptom_id):
    # Retrieve the symptom record based on the provided ID
    user_symptom = get_object_or_404(UserSymptoms, id=symptom_id)
    symptoms_text = user_symptom.symptoms  # Get symptoms text

    # Get AI recommendation based on symptoms
    recommendations = get_ai_recommendation(symptoms_text)
     # Save the recommendation in AnalysisResults for the current UserSymptoms instance
    analysis_result = AnalysisResults.objects.create(
        user_symptom=user_symptom,
        results=recommendations
    )

    # Pass the analysis result to the template to render on the webpage
    context = {'symptom': user_symptom, 'analysis_result': analysis_result}
    return render(request, 'Analysis.html', context)

# views.py

def submit_checkup(request):
    if request.method == "POST":
        # Access data submitted in the form
        checkup_data = request.POST.get("checkup_data")
        suggestions = request.POST.get("suggestions")
        notes = request.POST.get("notes")
        
        # Placeholder: Here you could save data to a database or process it
        # For now, let's just print the data to the console for testing
        print(f"Checkup Data: {checkup_data}")
        print(f"Suggestions: {suggestions}")
        print(f"Notes: {notes}")
        
        # Send a simple response back to confirm submission
        return render(request, "success_message.html")
    else:
        # If the request is GET, render the form template
        return render(request, "checkup.html")


def test_view(request):
    print("OpenAI API Key:", settings.OPENAI_API_KEY)
    return HttpResponse("Check your console for the API key!")

@login_required
def add_symptom(request):
    if request.method == "POST":
        symptom_text = request.POST.get("symptom")
        severity = request.POST.get("severity")  # Assuming you get severity from the form
        UserSymptoms.objects.create(user=request.user, symptoms=symptom_text, symptoms_severity=severity)
        messages.success(request, "Symptom recorded successfully.")
        return redirect('symptoms')  # Redirect back to symptoms page
    return render(request, 'add_symptom.html')  # Render form to add a symptom

# EDD calculation function
def calculate_edd(lmp_date):
    if lmp_date:
        try:
            return lmp_date + timedelta(days=280)  # Average gestational period (40 weeks)
        except Exception as e:
            print(f"Error calculating EDD: {e}")
    return None

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return redirect('dashboard')  # Redirect to the dashboard after marking as read
