from datetime import timedelta
from django.shortcuts import render, redirect
from application_tracking.enums import ApplicationStatus
from common.tasks import send_email
from accounts.models import User
from .forms import JobAdvertForm, JobApplicationForm
from django.http import HttpRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import JobAdvert, JobApplication
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q



@login_required
def create_advert(request: HttpRequest):
    form = JobAdvertForm(request.POST or None)
    
    if form.is_valid():
        instance: JobAdvert = form.save(commit=False)
        instance.created_by = request.user
        instance.save()
        
        messages.success(request, 'Advert created successfully. You can now receive applications.')
        return redirect(instance.get_absolute_url())
        
    context = {
        'job_advert_form': form,
        'title': 'Create a new Advert',
        'btn_text': 'Create Advert'
    }
    
    return render(request, 'create_advert.html', context)

def list_adverts(request: HttpRequest):
    active_jobs = JobAdvert.objects.active()
    
    paginator = Paginator(active_jobs, 10)
    request_page = request.GET.get('page')
    paginated_adverts = paginator.get_page(request_page)
    
    context = {
        'job_adverts': paginated_adverts
    }
    
    return render(request, 'home.html', context)
    
def get_advert(request: HttpRequest, advert_id):
    form = JobApplicationForm()
    job_advert = get_object_or_404(JobAdvert, id=advert_id)
    job_advert.skills_list = job_advert.skills.split(',') if job_advert.skills else []
    context = {
        'job_advert': job_advert,
        'application_form': form
    }
    return render(request, 'advert.html', context)
    
@login_required
def update_advert(request: HttpRequest, advert_id: int):
    advert = get_object_or_404(JobAdvert, pk=advert_id)
    if request.user != advert.created_by:
        return HttpResponseForbidden("You do not have permission to update this advert.")
    form = JobAdvertForm(request.POST or None, instance=advert)
    if form.is_valid():
        instance: JobAdvert = form.save(commit=False)
        instance.save()
        
        messages.success(request, 'Advert updated successfully.')
        return redirect(instance.get_absolute_url())
    
    context = {
        'job_advert_form': form,
        'btn_text': 'Update Advert'
    }
    return render(request, 'create_advert.html', context)

@login_required
def delete_advert(request: HttpRequest, advert_id: int):
    advert = get_object_or_404(JobAdvert, pk=advert_id)
    if request.user != advert.created_by:
        return HttpResponseForbidden("You do not have permission to delete this advert.")
    advert.delete()
    messages.success(request, 'Advert deleted successfully.')
    return redirect('my_jobs')

def apply(request: HttpRequest, advert_id: int):
    advert = get_object_or_404(JobAdvert, pk=advert_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            if advert.applications.filter(email__iexact=email).exists():
                messages.error(request, 'You have already applied for this job')
                return redirect('job_advert', advert_id=advert_id)
            application: JobApplication = form.save(commit=False)
            application.job_advert = advert
            application.save()
            messages.success(request, 'Application submitted successfully')
            return redirect('job_advert', advert_id=advert_id)
    else:
        form = JobApplicationForm()
        
    context = {
        'job_advert': advert,
        'application_form': form
    }
    
    return render(request, 'advert.html', context)

@login_required
def my_applications(request: HttpRequest):
    user: User = request.user
    
    applications = JobApplication.objects.filter(email = user.email)
    paginator = Paginator(applications, 10)
    request_page = request.GET.get('page')
    paginated_applications = paginator.get_page(request_page)
    
    context = {
        'my_applications': paginated_applications,
    }
    
    return render(request, 'my_applications.html', context)

@login_required
def my_jobs(request: HttpRequest):
    user: User = request.user
    today = timezone.now().date()
    jobs = JobAdvert.objects.filter(created_by = user)
    
    for job in jobs:
        if job.deadline:
            delta = job.deadline - today
            if delta.days > 30:
                job.time_left = f"{delta.days // 30} months left"
            elif delta.days > 0:
                job.time_left = f"{delta.days} days left"
            elif delta.days == 0:
                job.time_left = "Today"
            else:
                job.time_left = "Expired"
        else:
            job.time_left = "No deadline"

        
    
    paginator = Paginator(jobs, 10)
    request_page = request.GET.get('page')
    paginated_jobs = paginator.get_page(request_page)
    
    context = {
        'my_jobs': paginated_jobs,
        'current_date': timezone.now().date(),
    }
    
    return render(request, 'my_jobs.html', context)

@login_required
def advert_applications(request: HttpRequest, advert_id: int):
    advert: JobAdvert = get_object_or_404(JobAdvert, pk=advert_id)
    if request.user != advert.created_by:
        return HttpResponseForbidden("You do not have permission to view this page.")
    
    applications = advert.applications.all()
    # applications = JobApplication.objects.filter(job_advert = advert.id)
    paginator = Paginator(applications, 10)
    request_page = request.GET.get('page')
    paginated_applications = paginator.get_page(request_page)
    
    context = {
        'job_advert': advert,
        'applications': paginated_applications
    }
    
    return render(request, 'advert_applications.html', context)

@login_required
def decide(request: HttpRequest, job_application_id: int):
    job_application = get_object_or_404(JobApplication, pk=job_application_id)
    if request.user != job_application.job_advert.created_by:
        return HttpResponseForbidden("You do not have permission to view this page.")
    if request.method == 'POST':
        status = request.POST.get('status')
        job_application.status = status
        job_application.save(update_fields=['status'])
        messages.success(request, 'Application updated successfully.')
        
        if status == ApplicationStatus.REJECTED:
            context = {
                'applicant_name': job_application.name,
                'job_title': job_application.job_advert.title,
                'company_name': job_application.job_advert.company_name
            }
            send_email.delay(
                f'Application Outcome for {job_application.job_advert.title}',
                [job_application.email],
                'emails/job_application_update.html',
                context
            )
        elif status == ApplicationStatus.INTERVIEW:
            context = {
                'applicant_name': job_application.name,
                'job_title': job_application.job_advert.title,
                'company_name': job_application.job_advert.company_name,
            }
            send_email.delay(
                f'Interview Invitation for {job_application.job_advert.title}',
                [job_application.email],
                'emails/job_application_interview.html',
                context
            )
            
        return redirect('advert_applications', advert_id=job_application.job_advert.id)
    
def search(request: HttpRequest):
    keyword = request.GET.get('keyword')
    location = request.GET.get('location')
    result = JobAdvert.objects.search(keyword, location)
    
    paginator = Paginator(result, 10)
    request_page = request.GET.get('page')
    paginated_adverts = paginator.get_page(request_page)
    
    context = {
        'job_adverts': paginated_adverts
    }
    
    return render(request, 'home.html', context)