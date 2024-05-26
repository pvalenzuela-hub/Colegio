
from django.forms import ModelForm
from django import forms
from . models import Seguimiento, Personas, Ciclos, Colegio, Nivel, Curso, Area, Subarea, Asignatura, TipoRespuestaColegio, ResponsableSubareaNivel, CoordinadorCiclo, ProfesorJefe, ProfesorResponsable, ResponsableSuperior, AccesoColegio
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

class PersonasForm(ModelForm):
    class Meta:
        model = Personas
        fields = ["nombre","correo","telefono","cargo","esprofe","colegio"]
        
        widgets = {
                'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Nombre y apellido...'}),
                'correo': forms.EmailInput (attrs={'class': 'form-control','placeholder': 'Correo Electrónico...'}),
                'cargo': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Cargo...'}),
                'telefono': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Teléfono...'}),
                
        }

class CiclosForm(ModelForm):
    class Meta:
        model = Ciclos
        fields = ["nombre","colegio"]

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Nombre...'}),
        }

class ColegiosForm(ModelForm):
    class Meta:
        model = Colegio
        fields = ["nombre"]

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Colegio...'}),
        }

class NivelesForm(ModelForm):
    class Meta:
        model = Nivel
        fields = ['nombre','ciclo','orden']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Nivel...'}),
            'orden': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Orden...'}),
        }

class CursosForm(ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre','colegio','orden']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Curso...'}),
            'orden': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Orden...'}),
        }

class AreasForm(ModelForm):
    class Meta:
        model = Area
        fields = ['nombre','colegio']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Area...'}),
            
        }

class SubareasForm(ModelForm):
    class Meta:
        model = Subarea
        fields = ['nombre','area','profejefe']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Subarea...'}),
        }

class TiporespuestacolegioForm(ModelForm):
    class Meta:
        model = TipoRespuestaColegio
        fields = ['nombre']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Tipo respuesta...'}),
        }

class ResponsablesubareanivelForm(forms.ModelForm):
    class Meta:
        model = ResponsableSubareaNivel
        fields = ['persona', 'subarea', 'nivel']

    def __init__(self, *args, **kwargs):
        colegio_id = kwargs.pop('colegio_id', None)
        super(ResponsablesubareanivelForm, self).__init__(*args, **kwargs)
        
        if colegio_id:
            # Filtrado de persona (ejemplo: solo personas que son profesores)
            self.fields['persona'].queryset = Personas.objects.filter(colegio_id=colegio_id)
            
            # Filtrado de subarea (solo subáreas de un colegio específico)
            self.fields['subarea'].queryset = Subarea.objects.filter(area__colegio_id=colegio_id)
            
            # Filtrado de nivel (solo niveles de un colegio específico)
            self.fields['nivel'].queryset = Nivel.objects.filter(ciclo__colegio_id=colegio_id)


class CoordinadorcicloForm(ModelForm):
    class Meta:
        model = CoordinadorCiclo
        fields = ['persona','ciclo']

class ProfesorjefeForm(ModelForm):
    class Meta:
        model = ProfesorJefe
        fields = ['persona','nivel','curso']        

class ResponsableasignaturaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar las personas que sean profesores
        self.fields['persona'].queryset = Personas.objects.filter(esprofe=True)

    class Meta:
        model = ProfesorResponsable
        fields = ['persona','asignatura','nivel']

class ResponsablesuperiorForm(ModelForm):
   
    class Meta:
        model = ResponsableSuperior
        fields = ['persona','subarea']

class AccesoColegioForm(ModelForm):

    class Meta:
        model = AccesoColegio
        fields = ['colegiodefault','colegioactual']
