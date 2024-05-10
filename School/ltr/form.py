
from django.forms import ModelForm
from django import forms
from . models import Seguimiento
from django.contrib.auth.models import User
# Usuarios y contraseñas
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm

class SegForm(ModelForm):
    class Meta:
        model = Seguimiento
        fields = ['comentario']
        labels = { 'Ingresa aquí'}
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name','last_name','email','is_active', 'groups')
        # fields = "__all__"
        labels = ['Usuario','Nombre','Apellido','eMail','Es Activo']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput (attrs={'class': 'form-control'}),
            
        }

class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(label='Contraseña actual',widget=forms.PasswordInput(attrs={'class': 'form-control', 'type':'password'}))
    new_password1 = forms.CharField(label='Nueva contraseña',max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type':'password'}))
    new_password2 = forms.CharField(label='Nueva contraseña (Confirmación)',max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type':'password'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')
    
class CustomCreationForm(UserCreationForm):
    username = forms.CharField(label='RUT',widget=forms.TextInput(attrs={'class': 'form-control'}))
  

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2", "is_active"]


        widgets = {
                # 'username': forms.CharField(attrs={'class': 'form-control'}),
                'first_name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ingrese Nombre...'}),
                'last_name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ingrese Apellido...'}),
                'email': forms.EmailInput (attrs={'class': 'form-control','placeholder': 'Ingrese Correo Electrónico...'}),
                'password1': forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Ingrese contraseña...'}),
                'password2': forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Ingrese contraseña (Confirmación)...'}),
                
            }