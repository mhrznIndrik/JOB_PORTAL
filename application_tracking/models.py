from django.db import models
from common.models import BaseModel
from accounts.models import User
from .enums import EmploymentType, ExperienceLevel, LocationType, ApplicationStatus
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q

class JobAdvertQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_published=True, deadline__gte=timezone.now().date())
    
    def search(self, keyword, location):
        
        query = Q()

        if keyword:
            query &= (
                Q(title__icontains=keyword) 
                | Q(company_name__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(skills__icontains=keyword)
            )

        if location:
            query &= Q(location__icontains=location)

        return self.active().filter(query)
        

class JobAdvert(BaseModel):
    title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150)
    employment_type = models.CharField(max_length=50, choices=EmploymentType)
    experience_level = models.CharField(max_length=50, choices=ExperienceLevel)
    description = models.TextField()
    job_type = models.CharField(max_length=50, choices=LocationType)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    is_published = models.BooleanField(default=True)
    deadline = models.DateField()
    skills = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    objects = JobAdvertQuerySet.as_manager()

    class Meta:
        ordering = ('-created_at',)
        
    def publish_advert(self) -> None:
        self.is_published = True
        self.save(update_fields=['is_published'])
        
        
    @property
    def total_applicants(self) -> int:
        return self.applications.count()
    
    def get_absolute_url(self):
        return reverse("job_advert", kwargs={"advert_id": self.id})
    
        
class JobApplication(BaseModel):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    portfolio_url = models.URLField()
    cv = models.FileField(upload_to='cv/')
    status = models.CharField(max_length=50, choices=ApplicationStatus.choices, default=ApplicationStatus.APPLIED)
    job_advert = models.ForeignKey(JobAdvert, related_name='applications', on_delete=models.CASCADE)