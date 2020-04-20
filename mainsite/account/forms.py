from django import forms
from django.core.exceptions import ValidationError
from account.models import ItemPost 

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

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class CreateItemPostForm(forms.ModelForm):

    class Meta:
        model = ItemPost
        fields = ['title', 'body', 'price', 'inventory', 'image']


class UpdateItemPostForm(forms.ModelForm):

    class Meta:
        model = ItemPost
        fields = ['title', 'body', 'price', 'inventory', 'image']

    def save(self, commit=True):
        item_post = self.instance
        item_post.title = self.cleaned_data['title']
        item_post.body = self.cleaned_data['body']

        if self.cleaned_data['image']:
            item_post.image = self.cleaned_data['image']

        if commit:
            item_post.save()
        return item_post