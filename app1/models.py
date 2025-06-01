from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .validators import validate_unique_field
class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_time = models.DateTimeField(default=timezone.now)
    is_reset_allowed = models.BooleanField(default=False)

    def allow_reset(self):
        self.is_reset_allowed = True
        self.save()

    def __str__(self):
        return f"Password reset request for {self.user.username} at {self.request_time}"
    
class AdminNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username} - {self.created_at}"

from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Validators
alpha_validator = RegexValidator(
    regex=r'^[a-zA-Z ]*$',
    message='Only alphabetic characters and spaces are allowed.'
)
integer_validator = RegexValidator(
    regex=r'^[0-9]+$',
    message='Enter only integers.'
)

# BatchMaster table
BATCH_CHOICES = [
    (" ", "Select_Batch"),
    ("2020-2022", "2020-2022"),
    ("2021-2023", "2021-2023"),
    ("2022-2024", "2022-2024"),
    ("2023-2025", "2023-2025"),
    ("2024-2025", "2024-2025"),
    ("2025-2027", "2025-2027"),
    ("2026-2028", "2026-2028"),
    ("2027-2029", "2027-2029"),
    ("2028-2030", "2028-2030"),
]

class BatchMaster(models.Model):
    batchNo = models.CharField(max_length=2, validators=[integer_validator], unique=True)
    batchId = models.CharField(max_length=10, choices=BATCH_CHOICES, default=" ", unique=True)

    def __str__(self):
        return f'{self.batchId}'

    def clean(self):
        if not self.batchNo.isdigit():
            raise ValidationError("Batch number should contain only digits.")


# SemesterMaster table
SEM_CHOICES = [
    (" ", "Select_Semester"),
    ("I", "I"),
    ("II", "II"),
    ("III", "III"),
    ("IV", "IV"),
]

class SemesterMaster(models.Model):
    semester = models.CharField(max_length=15, choices=SEM_CHOICES, default=" ", blank=True)
    semesterId = models.CharField(max_length=6, validators=[integer_validator])

    def __str__(self):
        return f'{self.semester}'

    def clean(self):
        if not self.semesterId.isdigit():
            raise ValidationError("Semester ID should contain only digits.")


# StudentMaster table
CASTE_CHOICES = [
    (" ", "Select_Caste"),
    ("General", "General"),
    ("OBC", "OBC"),
    ("SC", "SC"),
    ("ST", "ST"),
]

COURSE_CHOICES = [
    (" ", "Select_Course"),
    ("B.Sc. Computer Science", "B.Sc. Computer Science"),
    ("B.Com", "B.Com"),
    ("B.A. English", "B.A. English"),
    ("B.Tech Civil Engineering", "B.Tech Civil Engineering"),
    ("B.Tech Mechanical Engineering", "B.Tech Mechanical Engineering"),
    ("B.Sc. Physics", "B.Sc. Physics"),
    ("B.Sc. Chemistry", "B.Sc. Chemistry"),
    ("B.A. Economics", "B.A. Economics"),
    ("BBA", "BBA"),
    ("MBA", "MBA"),
    ("MCA", "MCA"),
]

class StudentMaster(models.Model):
    batchNo = models.ForeignKey('BatchMaster', on_delete=models.CASCADE, related_name='students')
    sem = models.ForeignKey('SemesterMaster', on_delete=models.CASCADE, related_name='students')
    studentRegNo = models.CharField(max_length=10, validators=[integer_validator])
    studentName = models.CharField(max_length=50, validators=[alpha_validator])
    studentMobile = models.CharField(max_length=10, validators=[integer_validator])
    studentEmail = models.EmailField(max_length=55, unique=True)
    studentCaste = models.CharField(max_length=10, choices=CASTE_CHOICES, default=" ")
    course = models.CharField(max_length=50, choices=COURSE_CHOICES, default=" ")

    class Meta:
        unique_together = ('batchNo', 'sem', 'studentRegNo', 'studentName')

    def clean(self):
        if len(self.studentMobile) != 10:
            raise ValidationError("Mobile number must be exactly 10 digits.")

    def __str__(self):
        return f'{self.studentName} - {self.studentRegNo}'

####################################################################
from django.db import models
from django.core.exceptions import ValidationError

CERTIFICATE_STATUS_CHOICES = [
    ("Issued", "Issued"),
    ("Pending", "Pending"),
]

class CertificateMaster(models.Model):
    student = models.ForeignKey('StudentMaster', on_delete=models.CASCADE, related_name='certificates')
    certificateType = models.CharField(max_length=50)
    issueDate = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=CERTIFICATE_STATUS_CHOICES, default="Pending")


    def __str__(self):
        return f'{self.certificateType} - {self.status}'

    def clean(self):
        if self.status == "Issued" and not self.issueDate:
            raise ValidationError("Issue date is required for issued certificates.")




from django.db import models
from django.core.exceptions import ValidationError

class TransactionMaster(models.Model):
    student = models.ForeignKey('StudentMaster', on_delete=models.CASCADE, related_name='transactions')
    batchNo = models.ForeignKey('BatchMaster', on_delete=models.CASCADE, related_name='transactions')
    semester = models.ForeignKey('SemesterMaster', on_delete=models.CASCADE, related_name='transactions')
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Allow for up to 100.00
    issueDate = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=CERTIFICATE_STATUS_CHOICES, default="Pending")

    def clean(self):
        # Ensure the student belongs to the specified batch and semester
        if self.student.batchNo != self.batchNo:
            raise ValidationError("The student does not belong to the selected batch.")
        if self.student.sem != self.semester:
            raise ValidationError("The student is not enrolled in the selected semester.")

        # Validation for issued certificates
        if self.status == "Issued" and not self.issueDate:
            raise ValidationError("Issue date is required for issued transactions.")

    def __str__(self):
        return f'Transaction: {self.student.studentName} - {self.status}'

    class Meta:
        unique_together = ('student', 'batchNo', 'semester', 'marks', 'issueDate')
