from django import forms
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import re
from django import forms
from .models import PasswordResetRequest, AdminNotification
from django.core.exceptions import MultipleObjectsReturned
class PasswordResetRequestForm(forms.ModelForm):
    class Meta:
        model = PasswordResetRequest
        fields = ['user', 'is_reset_allowed']  # Adjust fields as necessary

class AdminNotificationForm(forms.ModelForm):
    class Meta:
        model = AdminNotification
        fields = ['user', 'message']  # Adjust fields as necessary

# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
        error_messages={
            'required': 'Username is required',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        error_messages={
            'required': 'Password is required',
        }
    )

    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        # Allow admin users to log in regardless of reset approval
        if user and user.is_staff:
            return password

        # Fetch the latest reset request for the user
        reset_requests = PasswordResetRequest.objects.filter(user=user).order_by('-request_time')

        if reset_requests.exists():
            latest_request = reset_requests.first()
            if not latest_request.is_reset_allowed:
                raise forms.ValidationError('Password reset is pending approval from admin.')

        if user is None:
            raise forms.ValidationError('Incorrect password')

        return password

class PasswordResetForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
        error_messages={
            'required': 'Username is required',
        }
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        error_messages={
            'required': 'New password is required',
        }
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        error_messages={
            'required': 'Confirmation password is required',
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

# Signup Form
class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        error_messages={
            'required': 'Password is required',
        }
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        error_messages={
            'required': 'Please confirm your password',
        }
    )

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isalpha():
            raise forms.ValidationError('Username should contain only alphabets')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username is already taken')
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Password should have a minimum length of 8 characters')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError('Password should contain at least one special character')
        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get('confirm_password')
        password = self.cleaned_data.get('password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your username'
    }))


from django import forms
from .models import *

class BatchMasterForm(forms.ModelForm):
    class Meta:
        model = BatchMaster
        fields = ['batchNo', 'batchId']
    
    def clean_batchNo(self):
        batchNo = self.cleaned_data.get('batchNo')
        if self.instance.pk:  # If updating an existing batch
            if BatchMaster.objects.filter(batchNo=batchNo).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(f"Batch No '{batchNo}' already exists.")
        else:  # If creating a new batch
            if BatchMaster.objects.filter(batchNo=batchNo).exists():
                raise forms.ValidationError(f"Batch No '{batchNo}' already exists.")
        return batchNo

    def clean_batchId(self):
        batchId = self.cleaned_data.get('batchId')
        if self.instance.pk:  # If updating an existing batch
            if BatchMaster.objects.filter(batchId=batchId).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(f"Batch ID '{batchId}' already exists.")
        else:  # If creating a new batch
            if BatchMaster.objects.filter(batchId=batchId).exists():
                raise forms.ValidationError(f"Batch ID '{batchId}' already exists.")
        return batchId

class SemesterMasterForm(forms.ModelForm):
    class Meta:
        model = SemesterMaster
        fields = ['semester', 'semesterId']
    
    def clean_semesterId(self):
        semester_id = self.cleaned_data.get('semesterId')
        if SemesterMaster.objects.filter(semesterId=semester_id).exists():
            raise forms.ValidationError("This Semester ID already exists. Please use a different one.")
        return semester_id

class StudentMasterForm(forms.ModelForm):
    class Meta:
        model = StudentMaster
        fields = ['batchNo', 'sem', 'studentRegNo', 'studentName', 'studentMobile', 'studentEmail',  'course']

    def clean_studentRegNo(self):
        student_reg_no = self.cleaned_data.get('studentRegNo')
        if StudentMaster.objects.filter(studentRegNo=student_reg_no).exists():
            raise forms.ValidationError("This Student Registration Number already exists. Please enter a unique one.")
        return student_reg_no

    def clean_studentName(self):
        student_name = self.cleaned_data.get('studentName')
        if StudentMaster.objects.filter(studentName=student_name).exists():
            raise forms.ValidationError("This Student Name already exists. Please enter a unique one.")
        return student_name

    def clean_studentMobile(self):
        student_mobile = self.cleaned_data.get('studentMobile')
        if StudentMaster.objects.filter(studentMobile=student_mobile).exists():
            raise forms.ValidationError("This Student Mobile Number already exists. Please enter a unique one.")
        return student_mobile

    def clean(self):
        cleaned_data = super().clean()
        batch_no = cleaned_data.get('batchNo')
        sem = cleaned_data.get('sem')
        student_reg_no = cleaned_data.get('studentRegNo')
        student_name = cleaned_data.get('studentName')
        student_mobile = cleaned_data.get('studentMobile')

        # You can add additional checks here if needed
        # For example, ensure that batchNo and semester are provided together

        return cleaned_data

#######################################################################
from django import forms
from .models import CertificateMaster

class CertificateMasterForm(forms.ModelForm):
    class Meta:
        model = CertificateMaster
        fields = ['student', 'certificateType', 'issueDate', 'status']

 
    
from django import forms
from .models import TransactionMaster

class TransactionMasterForm(forms.ModelForm):
    class Meta:
        model = TransactionMaster
        fields = ['student', 'batchNo', 'semester', 'marks', 'issueDate', 'status']