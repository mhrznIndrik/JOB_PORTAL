from django.db import models

EmploymentType = [
    ('Full Time', 'Full Time'),
    ('Part Time', 'Part Time'),
    ('Contract', 'Contract'),
    ('Internship', 'Internship'),
    ('Temporary', 'Temporary'),
    ('Volunteer', 'Volunteer'),
    ('Other', 'Other'),
] 

ExperienceLevel = [
    ('Entry Level', 'Entry Level'),
    ('Mid Level', 'Mid Level'),
    ('Senior Level', 'Senior Level'),
    ('Executive Level', 'Executive Level'),
    ('Other', 'Other'),
]

LocationType = [
    ('Onsite', 'Onsite'),
    ('Remote', 'Remote'),
    ('Hybrid', 'Hybrid'),
]

class ApplicationStatus(models.TextChoices):
    APPLIED = ('APPLIED', 'APPLIED')
    INTERVIEWE = ('INTERVIEWE', 'INTERVIEWE')
    REJECTED = ('REJECTED', 'REJECTED')
    HIRED = ('HIRED', 'HIRED')