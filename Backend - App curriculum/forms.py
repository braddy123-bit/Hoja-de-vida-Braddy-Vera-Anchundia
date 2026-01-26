

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from datetime import date
from .models import (
    DatosPersonales,
    ExperienciaLaboral,
    Reconocimiento,
    CursoRealizado,
    ProductoAcademico,
    ProductoLaboral,
    VentaGarage
)


# ======================================
# FORMULARIOS DE AUTENTICACIÓN
# ======================================

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True, label='Nombres')
    last_name = forms.CharField(max_length=100, required=True, label='Apellidos')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))


# ======================================
# FORMULARIO: DATOS PERSONALES
# ======================================

class DatosPersonalesForm(forms.ModelForm):
    class Meta:
        model = DatosPersonales
        fields = [
            'descripcionperfil', 'apellidos', 'nombres', 'nacionalidad',
            'lugarnacimiento', 'fechanacimiento', 'numerocedula', 'sexo',
            'estadocivil', 'licenciaconducir', 'telefonoconvencional',
            'telefonofijo', 'direcciontrabajo', 'direcciondomiciliaria',
            'sitioweb', 'foto',
            # Control de secciones PDF
            'mostrar_experiencia_pdf', 'mostrar_reconocimientos_pdf',
            'mostrar_cursos_pdf', 'mostrar_productos_academicos_pdf',
            'mostrar_productos_laborales_pdf', 'mostrar_venta_garage_pdf'
        ]
        widgets = {
            'descripcionperfil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mi Perfil Profesional'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control', 'value': 'Ecuatoriana'}),
            'lugarnacimiento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Quito, Ecuador'}),
            'fechanacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'max': date.today().isoformat()}),
            'numerocedula': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'estadocivil': forms.Select(attrs={'class': 'form-select'}),
            'licenciaconducir': forms.Select(attrs={'class': 'form-select'}),
            'telefonoconvencional': forms.TextInput(attrs={'class': 'form-control'}),
            'telefonofijo': forms.TextInput(attrs={'class': 'form-control'}),
            'direcciontrabajo': forms.TextInput(attrs={'class': 'form-control'}),
            'direcciondomiciliaria': forms.TextInput(attrs={'class': 'form-control'}),
            'sitioweb': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def clean_fechanacimiento(self):
        fecha = self.cleaned_data.get('fechanacimiento')
        if fecha > date.today():
            raise ValidationError('La fecha de nacimiento no puede ser futura')
        
        edad = date.today().year - fecha.year
        if edad < 15 or edad > 100:
            raise ValidationError('La edad debe estar entre 15 y 100 años')
        
        return fecha
    
    def clean_numerocedula(self):
        cedula = self.cleaned_data.get('numerocedula')
        if not cedula.isdigit():
            raise ValidationError('La cédula debe contener solo números')
        if len(cedula) != 10:
            raise ValidationError('La cédula debe tener 10 dígitos')
        return cedula


# ======================================
# FORMULARIO: EXPERIENCIA LABORAL
# ======================================

class ExperienciaLaboralForm(forms.ModelForm):
    class Meta:
        model = ExperienciaLaboral
        fields = [
            'cargodesempenado', 'nombrempresa', 'lugarempresa', 'emailempresa',
            'sitiowebempresa', 'nombrecontactoempresarial', 'telefonocontactoempresarial',
            'fechainiciogestion', 'fechafingestion', 'descripcionfunciones',
            'rutacertificado', 'activarparaqueseveaenfront'
        ]
        widgets = {
            'cargodesempenado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Desarrollador Full Stack'}),
            'nombrempresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la Empresa'}),
            'lugarempresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad, País'}),
            'emailempresa': forms.EmailInput(attrs={'class': 'form-control'}),
            'sitiowebempresa': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'nombrecontactoempresarial': forms.TextInput(attrs={'class': 'form-control'}),
            'telefonocontactoempresarial': forms.TextInput(attrs={'class': 'form-control'}),
            'fechainiciogestion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'max': date.today().isoformat()}),
            'fechafingestion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'max': date.today().isoformat()}),
            'descripcionfunciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rutacertificado': forms.FileInput(attrs={'class': 'form-control'}),
            'activarparaqueseveaenfront': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_fechainiciogestion(self):
        fecha = self.cleaned_data.get('fechainiciogestion')
        if fecha > date.today():
            raise ValidationError('La fecha de inicio no puede ser futura')
        return fecha
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fechainiciogestion')
        fecha_fin = cleaned_data.get('fechafingestion')
        
        if fecha_fin:
            # CORRIGE: No permite fechas futuras
            if fecha_fin > date.today():
                raise ValidationError({'fechafingestion': 'La fecha de finalización no puede ser futura'})
            
            # CORRIGE: Fecha fin debe ser posterior a fecha inicio
            if fecha_inicio and fecha_fin < fecha_inicio:
                raise ValidationError({'fechafingestion': 'La fecha de finalización no puede ser anterior a la fecha de inicio'})
        
        return cleaned_data


# ======================================
# FORMULARIO: RECONOCIMIENTOS
# ======================================

class ReconocimientoForm(forms.ModelForm):
    class Meta:
        model = Reconocimiento
        fields = [
            'tiporeconocimiento', 'fechareconocimiento', 'descripcionreconocimiento',
            'entidadpatrocinadora', 'nombrecontactoauspicia', 'telefonocontactoauspicia',
            'rutacertificado', 'activarparaqueseveaenfront'
        ]
        widgets = {
            'tiporeconocimiento': forms.Select(attrs={'class': 'form-select'}),
            'fechareconocimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'max': date.today().isoformat()}),
            'descripcionreconocimiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'entidadpatrocinadora': forms.TextInput(attrs={'class': 'form-control'}),
            'nombrecontactoauspicia': forms.TextInput(attrs={'class': 'form-control'}),
            'telefonocontactoauspicia': forms.TextInput(attrs={'class': 'form-control'}),
            'rutacertificado': forms.FileInput(attrs={'class': 'form-control'}),
            'activarparaqueseveaenfront': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_fechareconocimiento(self):
        fecha = self.cleaned_data.get('fechareconocimiento')
        # CORRIGE: No permite fechas futuras
        if fecha > date.today():
            raise ValidationError('La fecha del reconocimiento no puede ser futura. No puedes tener reconocimientos del futuro.')
        return fecha


# ======================================
# FORMULARIO: CURSOS REALIZADOS
# ======================================

class CursoRealizadoForm(forms.ModelForm):
    class Meta:
        model = CursoRealizado
        fields = [
            'nombrecurso', 'fechainicio', 'fechafin', 'totalhoras',
            'descripcioncurso', 'entidadpatrocinadora', 'nombrecontactoauspicia',
            'telefonocontactoauspicia', 'emailempresapatrocinadora',
            'rutacertificado', 'activarparaqueseveaenfront'
        ]
        widgets = {
            'nombrecurso': forms.TextInput(attrs={'class': 'form-control'}),
            'fechainicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'max': date.today().isoformat()}),
            'fechafin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'max': date.today().isoformat()}),
            'totalhoras': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'descripcioncurso': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'entidadpatrocinadora': forms.TextInput(attrs={'class': 'form-control'}),
            'nombrecontactoauspicia': forms.TextInput(attrs={'class': 'form-control'}),
            'telefonocontactoauspicia': forms.TextInput(attrs={'class': 'form-control'}),
            'emailempresapatrocinadora': forms.EmailInput(attrs={'class': 'form-control'}),
            'rutacertificado': forms.FileInput(attrs={'class': 'form-control'}),
            'activarparaqueseveaenfront': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_fechainicio(self):
        fecha = self.cleaned_data.get('fechainicio')
        # CORRIGE: Validación de fechas
        if fecha > date.today():
            raise ValidationError('La fecha de inicio no puede ser futura')
        return fecha
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fechainicio')
        fecha_fin = cleaned_data.get('fechafin')
        
        if fecha_fin:
            # CORRIGE: Validación completa de fechas
            if fecha_fin > date.today():
                raise ValidationError({'fechafin': 'La fecha de finalización no puede ser futura'})
            
            if fecha_inicio and fecha_fin < fecha_inicio:
                raise ValidationError({'fechafin': 'La fecha de finalización no puede ser anterior a la fecha de inicio'})
        
        return cleaned_data


# ======================================
# FORMULARIO: PRODUCTOS ACADÉMICOS
# ======================================

class ProductoAcademicoForm(forms.ModelForm):
    class Meta:
        model = ProductoAcademico
        fields = ['nombrerecurso', 'clasificador', 'descripcion', 'activarparaqueseveaenfront']
        widgets = {
            'nombrerecurso': forms.TextInput(attrs={'class': 'form-control'}),
            'clasificador': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Etiquetas separadas por comas. Ej: ingeniería,tecnologíainformación,basesdedatos,pregrado,docencia'
            }),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activarparaqueseveaenfront': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'clasificador': 'Ingresa etiquetas/palabras clave separadas por comas para clasificar el producto académico'
        }


# ======================================
# FORMULARIO: PRODUCTOS LABORALES
# ======================================

class ProductoLaboralForm(forms.ModelForm):
    class Meta:
        model = ProductoLaboral
        fields = ['nombreproducto', 'fechaproducto', 'descripcion', 'activarparaqueseveaenfront']
        widgets = {
            'nombreproducto': forms.TextInput(attrs={'class': 'form-control'}),
            'fechaproducto': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'max': date.today().isoformat()}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activarparaqueseveaenfront': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_fechaproducto(self):
        fecha = self.cleaned_data.get('fechaproducto')
        if fecha > date.today():
            raise ValidationError('La fecha del producto no puede ser futura')
        return fecha


# ======================================
# FORMULARIO: VENTA GARAGE
# ======================================

class VentaGarageForm(forms.ModelForm):
    class Meta:
        model = VentaGarage
        fields = [
            'nombreproducto', 'estadoproducto', 'descripcion', 'valordelbien',
            'fecha_publicacion', 'imagen_producto', 'activarparaqueseveaenfront'
        ]
        widgets = {
            'nombreproducto': forms.TextInput(attrs={'class': 'form-control'}),
            'estadoproducto': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valordelbien': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'fecha_publicacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': date.today().isoformat()}),
            'imagen_producto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'activarparaqueseveaenfront': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_valordelbien(self):
        valor = self.cleaned_data.get('valordelbien')
        if valor < 0:
            raise ValidationError('El valor no puede ser negativo')
        return valor


# ======================================
# FORMULARIO: SELECTOR DE SECCIONES PDF
# ======================================

class SelectorSeccionesPDFForm(forms.Form):
    """
    CORRIGE: Formulario para seleccionar qué secciones mostrar en el PDF
    """
    mostrar_experiencia = forms.BooleanField(required=False, initial=True, label='Experiencia Laboral')
    mostrar_reconocimientos = forms.BooleanField(required=False, initial=True, label='Reconocimientos')
    mostrar_cursos = forms.BooleanField(required=False, initial=True, label='Cursos Realizados')
    mostrar_productos_academicos = forms.BooleanField(required=False, initial=True, label='Productos Académicos')
    mostrar_productos_laborales = forms.BooleanField(required=False, initial=True, label='Productos Laborales')
    mostrar_venta_garage = forms.BooleanField(required=False, initial=True, label='Venta Garage')
    
    def __init__(self, *args, **kwargs):
        perfil = kwargs.pop('perfil', None)
        super().__init__(*args, **kwargs)
        
        if perfil:
            self.fields['mostrar_experiencia'].initial = perfil.mostrar_experiencia_pdf
            self.fields['mostrar_reconocimientos'].initial = perfil.mostrar_reconocimientos_pdf
            self.fields['mostrar_cursos'].initial = perfil.mostrar_cursos_pdf
            self.fields['mostrar_productos_academicos'].initial = perfil.mostrar_productos_academicos_pdf
            self.fields['mostrar_productos_laborales'].initial = perfil.mostrar_productos_laborales_pdf
            self.fields['mostrar_venta_garage'].initial = perfil.mostrar_venta_garage_pdf
