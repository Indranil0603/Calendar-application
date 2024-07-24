from django import forms
from .models import Activity
from django.core.exceptions import ValidationError
from django.utils import timezone

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity  # Use the Activity model
        fields = ['date', 'title', 'description']  # Fields to include in the form
        widgets = {
            'date': forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'type': 'date'})  # Use date input widget for 'date' field
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')  # Get cleaned date from form data
        if date < timezone.now().date():  # Check if date is in the past
            raise ValidationError("The date cannot be in the past.")  # Raise validation error if date is in the past
        return date
