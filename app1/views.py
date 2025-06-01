from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import PasswordResetRequestForm, AdminNotificationForm  
from .models import PasswordResetRequest, AdminNotification
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, SignupForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import loader
def admin_login(request):
    if request.method == 'POST':
        # Handle admin login logic here
        pass
    return render(request, 'admin_login.html')

def user_login(request):
    if request.method == 'POST':
        # Handle user login logic here
        pass
    return render(request, 'user_login.html')


@login_required  # Ensure the user is logged in
def admin_notifications(request):
    notifications = AdminNotification.objects.all().order_by('-created_at')  # Fetch all notifications
    return render(request, 'admin_notifications.html', {'notifications': notifications})

@login_required
def manage_password_reset_requests(request):
    # View all password reset requests
    requests = PasswordResetRequest.objects.all()
    return render(request, 'manage_password_reset_requests.html', {'requests': requests})

@login_required
def create_password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password reset request created successfully.")
            return redirect('manage_password_reset_requests')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'create_password_reset_request.html', {'form': form})

@login_required
def edit_password_reset_request(request, pk):
    reset_request = get_object_or_404(PasswordResetRequest, pk=pk)
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST, instance=reset_request)
        if form.is_valid():
            form.save()
            messages.success(request, "Password reset request updated successfully.")
            return redirect('manage_password_reset_requests')
    else:
        form = PasswordResetRequestForm(instance=reset_request)
    return render(request, 'edit_password_reset_request.html', {'form': form})

@login_required
def delete_password_reset_request(request, pk):
    reset_request = get_object_or_404(PasswordResetRequest, pk=pk)
    reset_request.delete()
    messages.success(request, "Password reset request deleted successfully.")
    return redirect('manage_password_reset_requests')

@login_required
def manage_admin_notifications(request):
    # View all admin notifications
    notifications = AdminNotification.objects.all()
    return render(request, 'manage_admin_notifications.html', {'notifications': notifications})

@login_required
def create_admin_notification(request):
    if request.method == 'POST':
        form = AdminNotificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin notification created successfully.")
            return redirect('manage_admin_notifications')
    else:
        form = AdminNotificationForm()
    return render(request, 'create_admin_notification.html', {'form': form})

@login_required
def edit_admin_notification(request, pk):
    notification = get_object_or_404(AdminNotification, pk=pk)
    if request.method == 'POST':
        form = AdminNotificationForm(request.POST, instance=notification)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin notification updated successfully.")
            return redirect('manage_admin_notifications')
    else:
        form = AdminNotificationForm(instance=notification)
    return render(request, 'edit_admin_notification.html', {'form': form})

@login_required
def delete_admin_notification(request, pk):
    notification = get_object_or_404(AdminNotification, pk=pk)
    notification.delete()
    messages.success(request, "Admin notification deleted successfully.")
    return redirect('manage_admin_notifications')

# Login view

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
from .forms import  PasswordResetForm
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.get(username=username)
            # Allow admin users to log in regardless of reset approval
            if user.is_staff:
                login(request, user)
                messages.success(request, "You have logged in successfully as admin.")
                return redirect('home')  # Redirect to home or another page
            # Fetch all PasswordResetRequests for the user
            reset_requests = PasswordResetRequest.objects.filter(user=user)
            # Check the latest reset request
            reset_allowed = any(req.is_reset_allowed for req in reset_requests)
            if not reset_allowed:
                messages.error(request, "You must reset your password before logging in.")
                return render(request, 'login.html', {'form': form})
            login(request, user)
            messages.success(request, "You have logged in successfully.")
            return redirect('home')  # Redirect to home or another page
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

from .forms import LoginForm, PasswordResetForm
def reset_password_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']
            # Set the new password for the user
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                # Update the PasswordResetRequest to allow logging in
                reset_request = PasswordResetRequest.objects.filter(user=user).order_by('-request_time').first()
                if reset_request:
                    reset_request.allow_reset()
                messages.success(request, "Your password has been reset successfully. You can now log in.")
                return redirect('login')
            except User.DoesNotExist:
                form.add_error(None, "User does not exist.")
    else:
        form = PasswordResetForm()

    return render(request, 'reset_password.html', {'form': form})
# Logout view
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

# Home view (for logged-in users)
@login_required
def homeDisplay(request):
    return render(request, "home.html")

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Signup successful. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Signup failed. Please correct the errors.")
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def forgot_password_request(request):
    if request.method == "POST":
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('forgot_password')
        
        # Create password reset request
        PasswordResetRequest.objects.create(user=user)
        
        # Notify admin
        AdminNotification.objects.create(
            user=user,
            message=f"{user.username} requested a password reset."
        )
        
        messages.success(request, "Password reset request submitted. Admin will respond.")
        return redirect('login')
    return render(request, 'forgot_password.html')

def admin_remove_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Set the user's password to None, requiring them to reset it
    user.set_password(None)
    user.save()
    
    # Update reset request and notify the user
    reset_request = get_object_or_404(PasswordResetRequest, user=user)
    reset_request.allow_reset()

    messages.success(request, f"Password for {user.username} removed. User can reset their password.")
    return redirect('admin_dashboard')

def user_reset_password(request):
    if request.method == "POST":
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('reset_password')
        
        # Check if the user is allowed to reset the password
        reset_request = get_object_or_404(PasswordResetRequest, user=user)
        
        if not reset_request.is_reset_allowed:
            messages.error(request, "You cannot reset the password yet.")
            return redirect('reset_password')
        
        # Validate new passwords
        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()

            # Mark the reset request as completed
            reset_request.delete()  # Optionally, you can mark it as completed instead of deleting it

            update_session_auth_hash(request, user)
            messages.success(request, "Password reset successfully.")
            return redirect('login')  # Redirect to login page
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, 'reset_password.html')


def reset_password_in_login(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the passwords match
        if new_password == confirm_password:
            # Validate the password (length, capital letter, number, special char)
            if not validate_password(new_password):
                messages.error(request, "Password does not meet criteria.")
                return redirect('reset_password_in_login', user_id=user.id)

            # Update the user's password
            user.set_password(new_password)
            user.save()

            # Mark the password reset request as completed
            reset_request = PasswordResetRequest.objects.get(user=user)
            reset_request.delete()  # Remove the request since it is now completed

            messages.success(request, "Password reset successful. Please log in.")
            return redirect('login')  # Redirect to login page
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, 'reset_password_in_login.html', {'user': user})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
def home2(request):
    return render(request, 'home2.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import BatchMaster
from .forms import BatchMasterForm

def batchmaster_list(request):
    batches = BatchMaster.objects.all()
    return render(request, 'batchmaster_list.html', {'batches': batches})

def batchmaster_create(request):
    if request.method == 'POST':
        form = BatchMasterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Batch created successfully!")
            return redirect('batchmaster_list')
        else:
            messages.error(request, "There were errors in the form. Please correct them.")
    else:
        form = BatchMasterForm()
    return render(request, 'batchmaster_form.html', {'form': form})

def batchmaster_update(request, pk):
    batch = get_object_or_404(BatchMaster, pk=pk)
    if request.method == 'POST':
        form = BatchMasterForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            messages.success(request, "Batch updated successfully!")
            return redirect('batchmaster_list')
        else:
            messages.error(request, "There were errors in the form. Please correct them.")
    else:
        form = BatchMasterForm(instance=batch)
    return render(request, 'batchmaster_form.html', {'form': form})

def batchmaster_delete(request, pk):
    batch = get_object_or_404(BatchMaster, pk=pk)
    if request.method == 'POST':
        batch.delete()
        messages.success(request, "Batch deleted successfully!")
        return redirect('batchmaster_list')
    return render(request, 'batchmaster_confirm_delete.html', {'batch': batch})

def batchmaster_search(request):
    query = request.GET.get('q')
    batches = BatchMaster.objects.filter(batchId__icontains=query) if query else BatchMaster.objects.all()
    return render(request, 'batchmaster_list.html', {'batches': batches})

from django.shortcuts import render
from .models import BatchMaster

def batchmaster_report(request):
    batches = BatchMaster.objects.all()  # Default to all batches
    error_message = None

    if request.method == 'POST':
        search_value = request.POST.get('search_value', '').strip()

        if search_value:  # Check if search value is provided
            batches = BatchMaster.objects.filter(batchNo__icontains=search_value)

            if not batches.exists():  # Check if any batches were found
                error_message = "No batches found with that Batch No."

    return render(request, 'batchmaster_report.html', {'batches': batches, 'error_message': error_message})



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import SemesterMaster
from .forms import SemesterMasterForm
from django.contrib import messages

def semester_list(request):
    semesters = SemesterMaster.objects.all()
    return render(request, 'semester_list.html', {'semesters': semesters})

def semester_create(request):
    if request.method == "POST":
        form = SemesterMasterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Semester created successfully!")
            return redirect('semester_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SemesterMasterForm()
    return render(request, 'semester_form.html', {'form': form})

def semester_update(request, pk):
    semester = get_object_or_404(SemesterMaster, pk=pk)
    if request.method == "POST":
        form = SemesterMasterForm(request.POST, instance=semester)
        if form.is_valid():
            form.save()
            messages.success(request, "Semester updated successfully!")
            return redirect('semester_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SemesterMasterForm(instance=semester)
    return render(request, 'semester_form.html', {'form': form})

def semester_delete(request, pk):
    semester = get_object_or_404(SemesterMaster, pk=pk)
    if request.method == "POST":
        semester.delete()
        messages.success(request, "Semester deleted successfully!")
        return redirect('semester_list')
    return render(request, 'semester_confirm_delete.html', {'semester': semester})

def semester_search(request):
    query = request.GET.get('q')
    if query:
        semesters = SemesterMaster.objects.filter(semesterId__icontains=query)
    else:
        semesters = SemesterMaster.objects.all()
    return render(request, 'semester_list.html', {'semesters': semesters})


from django.utils import timezone

def semester_report(request, pk=None):
    current_time = timezone.now()
    if pk:
        # Fetch specific semester record
        semester = get_object_or_404(SemesterMaster, pk=pk)
        semesters = [semester]  # Create a list with a single item for display
        report_title = f"Report for Semester {semester.semester}"
    else:
        # Fetch all semester records
        semesters = SemesterMaster.objects.all()
        report_title = "Report for All Semesters"

    return render(request, 'semester_report.html', {
        'semesters': semesters,
        'report_title': report_title,
        'current_time': current_time,
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import StudentMaster
from .forms import StudentMasterForm
from django.contrib import messages

# View to list all students in sorted order
def student_list(request):
    students = StudentMaster.objects.all().order_by('studentRegNo')  # Adjust sorting as needed
    return render(request, 'student_list.html', {'students': students})

def student_create(request):
    if request.method == "POST":
        form = StudentMasterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student created successfully!")
            return redirect('student_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentMasterForm()
    return render(request, 'student_form.html', {'form': form})

def student_update(request, pk):
    student = get_object_or_404(StudentMaster, pk=pk)
    if request.method == "POST":
        form = StudentMasterForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully!")
            return redirect('student_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentMasterForm(instance=student)
    return render(request, 'student_form.html', {'form': form})

def student_delete(request, pk):
    student = get_object_or_404(StudentMaster, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully!")
        return redirect('student_list')
    return render(request, 'student_confirm_delete.html', {'student': student})

def student_search(request):
    query = request.GET.get('q')
    if query:
        students = StudentMaster.objects.filter(studentName__icontains=query).order_by('studentName')  # Sort results
    else:
        students = StudentMaster.objects.all().order_by('studentName')  # Sort all records
    return render(request, 'student_list.html', {'students': students})

# Report view, if needed for generating reports
from django.utils import timezone

def student_report(request, pk=None):
    current_time = timezone.now()

    query = request.GET.get('q')  # Get the search query from the request (studentRegNo)

    if query:
        # Filter students by studentRegNo
        students = StudentMaster.objects.filter(studentRegNo__icontains=query).order_by('studentRegNo')
        if not students:
            error_message = f"No students found with Registration Number: {query}"
        else:
            error_message = None
        report_title = f"Search Results for {query}"
    else:
        if pk:
            # Fetch specific student record by pk
            student = get_object_or_404(StudentMaster, pk=pk)
            students = [student]  # Create a list with a single item for display
            report_title = f"Report for Student {student.studentName}"
        else:
            # Fetch all student records if no pk or search query is provided
            students = StudentMaster.objects.all().order_by('studentRegNo')
            report_title = "Report for All Students"
        error_message = None

    return render(request, 'student_report.html', {
        'students': students,
        'report_title': report_title,
        'current_time': current_time,
        'error_message': error_message,
    })

#################################################################

from django.shortcuts import render, redirect, get_object_or_404
from .models import CertificateMaster, StudentMaster
from .forms import CertificateMasterForm
from django.contrib import messages

def certificate_list(request):
    certificates = CertificateMaster.objects.all().order_by('certificateType')
    return render(request, 'certificate_list.html', {'certificates': certificates})

def certificate_create(request):
    if request.method == "POST":
        form = CertificateMasterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Certificate created successfully!")
            return redirect('certificate_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CertificateMasterForm()
    return render(request, 'certificate_form.html', {'form': form})

def certificate_update(request, pk):
    certificate = get_object_or_404(CertificateMaster, pk=pk)
    if request.method == "POST":
        form = CertificateMasterForm(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            messages.success(request, "Certificate updated successfully!")
            return redirect('certificate_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CertificateMasterForm(instance=certificate)
    return render(request, 'certificate_form.html', {'form': form})

def certificate_delete(request, pk):
    certificate = get_object_or_404(CertificateMaster, pk=pk)
    if request.method == "POST":
        certificate.delete()
        messages.success(request, "Certificate deleted successfully!")
        return redirect('certificate_list')
    return render(request, 'certificate_confirm_delete.html', {'certificate': certificate})

def certificate_search(request):
    query = request.GET.get('q')
    if query:
        certificates = CertificateMaster.objects.filter(certificateType__icontains=query).order_by('certificateType')
    else:
        certificates = CertificateMaster.objects.all().order_by('certificateType')
    return render(request, 'certificate_list.html', {'certificates': certificates})
###################################################################
def certificate_report(request, pk=None):
    """
    View to generate a report of certificates. If a specific primary key (pk) is provided,
    it fetches the corresponding certificate. Otherwise, it fetches all certificates.
    """
    current_time = timezone.now()
    query = request.GET.get('q')  # Get the search query from the request (certificate ID or Name)

    if query:
        # Filter certificates by ID or name (adjust filter field based on your model)
        certificates = CertificateMaster.objects.filter(certificateId__icontains=query)
        if not certificates:
            error_message = f"No certificates found with ID: {query}"
        else:
            error_message = None
        report_title = f"Search Results for {query}"
    else:
        if pk:
            # Fetch specific certificate record by pk
            certificate = get_object_or_404(CertificateMaster, pk=pk)
            certificates = [certificate]  # Create a list with a single item for display
            report_title = f"Report for Certificate {certificate.certificateName}"
        else:
            # Fetch all certificate records if no pk or search query is provided
            certificates = CertificateMaster.objects.all()
            report_title = "Report for All Certificates"
        error_message = None

    return render(request, 'certificate_report.html', {
        'certificates': certificates,
        'report_title': report_title,
        'current_time': current_time,
        'error_message': error_message,
    })

###########################################################################

import os
import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import BatchMaster, SemesterMaster, StudentMaster, CertificateMaster
from django.contrib import messages
from django.core.files.storage import default_storage

# Backup View
def backup_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=backup_data.csv'

    writer = csv.writer(response)
    writer.writerow(['Model', 'Field Names', 'Data'])

    # Backup BatchMaster
    batches = BatchMaster.objects.all()
    for batch in batches:
        writer.writerow(['BatchMaster', batch.batchId, batch.batchNo])

    # Backup SemesterMaster
    semesters = SemesterMaster.objects.all()
    for semester in semesters:
        writer.writerow(['SemesterMaster', semester.semester, semester.semesterId])

    # Backup StudentMaster
    students = StudentMaster.objects.all()
    for student in students:
        writer.writerow([
            'StudentMaster', student.studentName, student.studentRegNo,
            student.studentMobile, student.studentEmail, student.course
        ])

    # Backup CertificateMaster
    certificates = CertificateMaster.objects.all()
    for cert in certificates:
        writer.writerow([
            'CertificateMaster', cert.student.studentName, cert.certificateType,
            cert.issueDate, cert.status
        ])

    return response

# Restore View
def restore_data(request):
    if request.method == 'POST' and request.FILES['restore_file']:
        restore_file = request.FILES['restore_file']
        file_path = default_storage.save(restore_file.name, restore_file)
        file_path_full = default_storage.path(file_path)

        try:
            with open(file_path_full, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    model_name, *data = row

                    if model_name == 'BatchMaster':
                        BatchMaster.objects.create(batchId=data[0], batchNo=data[1])
                    elif model_name == 'SemesterMaster':
                        SemesterMaster.objects.create(semester=data[0], semesterId=data[1])
                    elif model_name == 'StudentMaster':
                        StudentMaster.objects.create(
                            studentName=data[0], studentRegNo=data[1],
                            studentMobile=data[2], studentEmail=data[3], course=data[4]
                        )
                    elif model_name == 'CertificateMaster':
                        student = StudentMaster.objects.get(studentName=data[0])
                        CertificateMaster.objects.create(
                            student=student, certificateType=data[1],
                            issueDate=data[2], status=data[3]
                        )
            messages.success(request, "Data restored successfully!")
        except Exception as e:
            messages.error(request, f"Error during restore: {e}")
        finally:
            default_storage.delete(file_path)

        return redirect('backup_restore')
    return render(request, 'restore_data.html')



from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import TransactionMaster
from .forms import TransactionMasterForm  # Assume a form is created for TransactionMaster

from django.db.models import Q
import csv

# List View
def transaction_list(request):
    query = request.GET.get('q')
    transactions = TransactionMaster.objects.all()

    if query:
        transactions = transactions.filter(
            Q(student__studentName__icontains=query) |
            Q(batchNo__batchId__icontains=query) |
            Q(semester__semester__icontains=query) |
            Q(status__icontains=query)
        )
    
    return render(request, 'transaction_list.html', {'transactions': transactions})

# Create View
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionMasterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionMasterForm()
    
    return render(request, 'transaction_form.html', {'form': form})

# Update View
def transaction_update(request, pk):
    transaction = get_object_or_404(TransactionMaster, pk=pk)
    if request.method == 'POST':
        form = TransactionMasterForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionMasterForm(instance=transaction)
    
    return render(request, 'transaction_form.html', {'form': form})

# Delete View
def transaction_delete(request, pk):
    transaction = get_object_or_404(TransactionMaster, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')
    
    return render(request, 'transaction_confirm_delete.html', {'transaction': transaction})

# # Report Generation
# def transaction_report(request):
#     transactions = TransactionMaster.objects.all()
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="transaction_report.csv"'

#     writer = csv.writer(response)
#     writer.writerow(['Student Name', 'Batch No', 'Semester', 'Marks', 'Issue Date', 'Status'])

#     for transaction in transactions:
#         writer.writerow([
#             transaction.student.studentName,
#             transaction.batchNo.batchId,
#             transaction.semester.semester,
#             transaction.marks,
#             transaction.issueDate,
#             transaction.status
#         ])

#     return response
import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from .models import TransactionMaster

def transaction_report(request, pk=None):
    """
    View to generate a report of transactions. If a specific primary key (pk) is provided,
    it fetches the corresponding transaction. Otherwise, it fetches all transactions.
    """
    current_time = timezone.now()
    query = request.GET.get('q')  # Get the search query from the request (Transaction ID or Name)

    if query:
        # Filter transactions by ID or Student Name (adjust filter field based on your model)
        transactions = TransactionMaster.objects.filter(student__studentName__icontains=query)
        if not transactions:
            error_message = f"No transactions found for: {query}"
        else:
            error_message = None
        report_title = f"Search Results for {query}"
    else:
        if pk:
            # Fetch specific transaction record by pk
            transaction = get_object_or_404(TransactionMaster, pk=pk)
            transactions = [transaction]  # Create a list with a single item for display
            report_title = f"Report for Transaction ID {transaction.id}"
        else:
            # Fetch all transaction records if no pk or search query is provided
            transactions = TransactionMaster.objects.all()
            report_title = "Report for All Transactions"
        error_message = None

    return render(request, 'transaction_report.html', {
        'transactions': transactions,
        'report_title': report_title,
        'current_time': current_time,
        'error_message': error_message,
    })


# Export Transactions as CSV
def export_transaction_report(request):
    """
    View to generate and download transaction report as a CSV file.
    """
    transactions = TransactionMaster.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transaction_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Batch No', 'Semester', 'Marks', 'Issue Date', 'Status'])

    for transaction in transactions:
        writer.writerow([
            transaction.student.studentName,
            transaction.batchNo.batchId,
            transaction.semester.semester,
            transaction.marks,
            transaction.issueDate,
            transaction.status
        ])

    return response
