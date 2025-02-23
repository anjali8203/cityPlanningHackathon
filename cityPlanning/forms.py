from django import forms
from .models import Message, Project

class ProjectForm(forms.ModelForm):
    CITY_CHOICES = [
        ("", "Select a city"),  # Default empty option
        ("charlottesville", "Charlottesville"),
        ("madrid", "Madrid"),
        # Add more cities as needed
    ]

    city = forms.ChoiceField(choices=CITY_CHOICES, required=True, label="Select a City")

    class Meta:
        model = Project
        fields = ['title', 'description', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'placeholder': 'Enter the project title',
            'class': 'form-control',
            'style': 'margin-bottom: 1rem;'
        })
        self.fields['description'].widget.attrs.update({
            'placeholder': 'Provide a detailed description of the project',
            'class': 'form-control',
            'style': 'margin-bottom: 1rem;'
        })
        self.fields['location'].widget.attrs.update({
            'placeholder': 'Provide a location',
            'class': 'form-control',
            'style': 'margin-bottom: 1rem;'
        })

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Write your message here...',
            'class': 'form-control',
            'style': 'margin-bottom: 1rem;'
        })
