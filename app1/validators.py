# myapp/validators.py
from django import forms

def validate_unique_field(model, field_name, value, exclude_id=None):
    queryset = model.objects.filter(**{field_name: value})
    if exclude_id:
        queryset = queryset.exclude(pk=exclude_id)
    if queryset.exists():
        raise forms.ValidationError(f"{field_name.replace('_', ' ').capitalize()} '{value}' already exists.")
