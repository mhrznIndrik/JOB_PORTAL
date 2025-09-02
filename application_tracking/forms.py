from django.forms import ModelForm
from .models import JobAdvert, JobApplication
from django import forms


class JobAdvertForm(ModelForm):
    class Meta:
        model = JobAdvert
        fields = [
            'title',
            'company_name',
            'employment_type',
            'experience_level',
            'job_type',
            'location',
            'description',
            'skills',
            'salary',
            'is_published',
            'deadline',
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g., Senior Software Engineer',
                'class': 'form-input w-full rounded-lg border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'company_name': forms.TextInput(attrs={
                'placeholder': 'e.g., TechCorp Inc.',
                'class': 'form-input w-full rounded-lg border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g., Lalitpur',
                'class': 'form-input w-full rounded-lg border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'salary': forms.NumberInput(attrs={
                'placeholder': 'e.g., Rs.80000 - Rs.120000',
                'class': 'form-input w-full rounded-lg border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-input w-full md:w-64 rounded-lg border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'skills': forms.TextInput(attrs={
                'placeholder': 'e.g., Python, React, AWS, Docker',
                'class': 'form-input w-full rounded-lg border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Provide a detailed description of the role, responsibilities, and requirements...',
                'class': 'form-textarea w-full rounded-lg border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 6
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
        }
        
class JobApplicationForm(ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            'name',
            'email',
            'portfolio_url',
            'cv',
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200'}),
            'portfolio_url': forms.URLInput(attrs={'placeholder': 'Portfolio Link', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200'}),
            'cv': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white', 'accept': '.pdf,.doc,.docx', 'placeholder': 'Upload CV'}),
        }