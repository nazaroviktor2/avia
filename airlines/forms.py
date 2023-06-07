from django import forms
from django.contrib.auth.models import User

from airlines.models import Client

MAX_LEN = 150


class ClientRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=MAX_LEN, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def clean_confirm(self):
        password = self.cleaned_data.get('password')
        confirm = self.cleaned_data.get('confirm')

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return confirm

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Check if the username exists in the User model
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different username.')

        # Check if the username exists in the Client model
        if Client.objects.filter(user__username=username).exists():
            raise forms.ValidationError('A client with this username already exists.')

        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

        client = Client(user=user)
        client.save()
        return user
