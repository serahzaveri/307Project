from django import forms
from django.core.exceptions import ValidationError

class SignupForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    age = forms.IntegerField(required=False)
    password = forms.CharField()
    password_confirm = forms.CharField()
    
    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        
        # Validation involving multiple fields
        if 'password' in cleaned_data and 'password_confirm' in cleaned_data and cleaned_data['password'] != cleaned_data['password_confirm']:
            self.add_error('password_confirm', 'Passwords do not match')
        return cleaned_data
