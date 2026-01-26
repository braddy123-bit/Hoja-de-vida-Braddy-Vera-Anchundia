
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from datetime import date
import uuid


# ======================================
# VALIDADORES PERSONALIZADOS
# ======================================

def validar_fecha_pasada(value):
    """No permite fechas futuras"""
    if value > date.today():
        raise ValidationError('La fecha no puede ser futura')


def validar_fecha_nacimiento(value):
    """Valida fecha de nacimiento razonable"""
    if value > date.today():
        raise ValidationError('La fecha de nacimiento no puede ser futura')
    
    edad = date.today().year - value.year
    if edad < 15 or edad > 100:
        raise ValidationError('La edad debe estar entre 15 y 100 años')


def validar_fecha_fin_posterior(fecha_inicio):
    """Validador para fecha fin"""
    def validator(value):
        if value and fecha_inicio and value < fecha_inicio:
            raise ValidationError('La fecha de finalización no puede ser anterior a la fecha de inicio')
    return validator


# ======================================
# MODELO: DATOS PERSONALES
# ======================================

class DatosPersonales(models.Model):
    """
    Tabla principal de datos personales
    Mapea: DATOSPERSONALES
    """
    SEXO_CHOICES = [
        ('H', 'Hombre'),
        ('M', 'Mujer'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('Soltero/a', 'Soltero/a'),
        ('Casado/a', 'Casado/a'),
        ('Divorciado/a', 'Divorciado/a'),
        ('Viudo/a', 'Viudo/a'),
        ('Unión Libre', 'Unión Libre'),
    ]
    
    LICENCIA_CHOICES = [
        ('A', 'Tipo A'),
        ('B', 'Tipo B'),
        ('C', 'Tipo C'),
        ('D', 'Tipo D'),
        ('E', 'Tipo E'),
        ('F', 'Tipo F'),
        ('G', 'Tipo G'),
        ('NINGUNA', 'No posee'),
    ]
    
    # Campos de la tabla original
    idperfil = models.AutoField(primary_key=True, db_column='idperfil')
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='datos_personales')
    
    descripcionperfil = models.CharField(max_length=50, verbose_name='Descripción del Perfil', default='Mi Perfil Profesional')
    perfilactivo = models.IntegerField(default=1, verbose_name='Perfil Activo')
    
    # Información personal
    apellidos = models.CharField(max_length=60, verbose_name='Apellidos')
    nombres = models.CharField(max_length=60, verbose_name='Nombres')
    nacionalidad = models.CharField(max_length=20, default='Ecuatoriana', verbose_name='Nacionalidad')
    lugarnacimiento = models.CharField(max_length=60, verbose_name='Lugar de Nacimiento')
    fechanacimiento = models.DateField(verbose_name='Fecha de Nacimiento', validators=[validar_fecha_nacimiento])
    numerocedula = models.CharField(max_length=10, unique=True, verbose_name='Número de Cédula')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name='Sexo')
    estadocivil = models.CharField(max_length=50, choices=ESTADO_CIVIL_CHOICES, verbose_name='Estado Civil')
    licenciaconducir = models.CharField(max_length=6, choices=LICENCIA_CHOICES, default='NINGUNA', verbose_name='Licencia de Conducir')
    
    # Contacto
    telefonoconvencional = models.CharField(max_length=15, blank=True, verbose_name='Teléfono Convencional')
    telefonofijo = models.CharField(max_length=15, blank=True, verbose_name='Teléfono Fijo')
    direcciontrabajo = models.CharField(max_length=50, blank=True, verbose_name='Dirección de Trabajo')
    direcciondomiciliaria = models.CharField(max_length=50, verbose_name='Dirección Domiciliaria')
    sitioweb = models.URLField(max_length=60, blank=True, verbose_name='Sitio Web')
    
    # Campos adicionales para el sistema
    foto = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name='Foto de Perfil')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    # Secciones visibles en PDF (CORRIGE ERROR: falta opción para apagar secciones)
    mostrar_experiencia_pdf = models.BooleanField(default=True, verbose_name='Mostrar Experiencia en PDF')
    mostrar_reconocimientos_pdf = models.BooleanField(default=True, verbose_name='Mostrar Reconocimientos en PDF')
    mostrar_cursos_pdf = models.BooleanField(default=True, verbose_name='Mostrar Cursos en PDF')
    mostrar_productos_academicos_pdf = models.BooleanField(default=True, verbose_name='Mostrar Productos Académicos en PDF')
    mostrar_productos_laborales_pdf = models.BooleanField(default=True, verbose_name='Mostrar Productos Laborales en PDF')
    mostrar_venta_garage_pdf = models.BooleanField(default=True, verbose_name='Mostrar Venta Garage en PDF')
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'datospersonales'
        verbose_name = 'Datos Personales'
        verbose_name_plural = 'Datos Personales'
        ordering = ['-fecha_actualizacion']
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.nombres.lower()}-{self.apellidos.lower()}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def edad(self):
        hoy = date.today()
        edad = hoy.year - self.fechanacimiento.year
        if hoy.month < self.fechanacimiento.month or (hoy.month == self.fechanacimiento.month and hoy.day < self.fechanacimiento.day):
            edad -= 1
        return edad


# ======================================
# MODELO: EXPERIENCIA LABORAL
# ======================================

class ExperienciaLaboral(models.Model):
    """
    Tabla de experiencia laboral
    Mapea: EXPERIENCIALABORAL
    CORRIGE: Validación de fechas, orden cronológico
    """
    idexperiencilaboral = models.AutoField(primary_key=True, db_column='idexperiencilaboral')
    idperfilconqueestaactivo = models.ForeignKey(
        DatosPersonales, 
        on_delete=models.CASCADE, 
        related_name='experiencias_laborales',
        db_column='idperfilconqueestaactivo'
    )
    
    # Información del cargo
    cargodesempenado = models.CharField(max_length=100, verbose_name='Cargo Desempeñado')
    nombrempresa = models.CharField(max_length=50, verbose_name='Nombre de la Empresa')
    lugarempresa = models.CharField(max_length=50, verbose_name='Lugar de la Empresa')
    emailempresa = models.EmailField(max_length=100, blank=True, verbose_name='Email de la Empresa')
    sitiowebempresa = models.URLField(max_length=100, blank=True, verbose_name='Sitio Web de la Empresa')
    
    # Contacto empresarial
    nombrecontactoempresarial = models.CharField(max_length=100, blank=True, verbose_name='Nombre de Contacto')
    telefonocontactoempresarial = models.CharField(max_length=60, blank=True, verbose_name='Teléfono de Contacto')
    
    # Fechas (CORREGIDO: validación de fechas)
    fechainiciogestion = models.DateField(verbose_name='Fecha de Inicio', validators=[validar_fecha_pasada])
    fechafingestion = models.DateField(null=True, blank=True, verbose_name='Fecha de Fin')
    
    # Descripción
    descripcionfunciones = models.TextField(verbose_name='Descripción de Funciones')
    
    # Control de visibilidad
    activarparaqueseveaenfront = models.BooleanField(default=True, verbose_name='Activar para Front')
    
    # Certificado
    rutacertificado = models.FileField(
        upload_to='certificados/experiencia/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name='Certificado'
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'experiencialaboral'
        verbose_name = 'Experiencia Laboral'
        verbose_name_plural = 'Experiencias Laborales'
        ordering = ['-fechainiciogestion']  # CORREGIDO: Orden cronológico de más reciente a antigua
    
    def __str__(self):
        return f"{self.cargodesempenado} en {self.nombrempresa}"
    
    def clean(self):
        # CORRIGE: Validación de fechas
        if self.fechafingestion:
            if self.fechafingestion > date.today():
                raise ValidationError({'fechafingestion': 'La fecha de finalización no puede ser futura'})
            
            if self.fechafingestion < self.fechainiciogestion:
                raise ValidationError({'fechafingestion': 'La fecha de finalización no puede ser anterior a la fecha de inicio'})


# ======================================
# MODELO: RECONOCIMIENTOS
# ======================================

class Reconocimiento(models.Model):
    """
    Tabla de reconocimientos
    Mapea: RECONOCIMIENTOS
    CORRIGE: Validación de fechas, orden cronológico
    """
    TIPO_CHOICES = [
        ('Académico', 'Académico'),
        ('Público', 'Público'),
        ('Privado', 'Privado'),
    ]
    
    idreconocimiento = models.AutoField(primary_key=True, db_column='idreconocimiento')
    idperfilconqueestaactivo = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        related_name='reconocimientos',
        db_column='idperfilconqueestaactivo'
    )
    
    tiporeconocimiento = models.CharField(max_length=100, choices=TIPO_CHOICES, verbose_name='Tipo de Reconocimiento')
    fechareconocimiento = models.DateField(verbose_name='Fecha del Reconocimiento', validators=[validar_fecha_pasada])
    descripcionreconocimiento = models.TextField(verbose_name='Descripción')
    
    # Entidad patrocinadora
    entidadpatrocinadora = models.CharField(max_length=100, verbose_name='Entidad Patrocinadora')
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, verbose_name='Nombre de Contacto')
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, verbose_name='Teléfono de Contacto')
    
    # Control
    activarparaqueseveaenfront = models.BooleanField(default=True, verbose_name='Activar para Front')
    
    # Certificado
    rutacertificado = models.FileField(
        upload_to='certificados/reconocimientos/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name='Certificado'
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reconocimientos'
        verbose_name = 'Reconocimiento'
        verbose_name_plural = 'Reconocimientos'
        ordering = ['-fechareconocimiento']  # CORREGIDO: Orden cronológico
    
    def __str__(self):
        return f"{self.tiporeconocimiento} - {self.entidadpatrocinadora}"
    
    def clean(self):
        # CORRIGE: No permite fechas futuras
        if self.fechareconocimiento > date.today():
            raise ValidationError({'fechareconocimiento': 'La fecha del reconocimiento no puede ser futura'})


# ======================================
# MODELO: CURSOS REALIZADOS
# ======================================

class CursoRealizado(models.Model):
    """
    Tabla de cursos realizados
    Mapea: CURSOSREALIZADOS
    CORRIGE: Validación de fechas
    """
    idcursorealizado = models.AutoField(primary_key=True, db_column='idcursorealizado')
    idperfilconqueestaactivo = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        related_name='cursos_realizados',
        db_column='idperfilconqueestaactivo'
    )
    
    nombrecurso = models.CharField(max_length=100, verbose_name='Nombre del Curso')
    fechainicio = models.DateField(verbose_name='Fecha de Inicio', validators=[validar_fecha_pasada])
    fechafin = models.DateField(verbose_name='Fecha de Fin')
    totalhoras = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Total de Horas')
    
    descripcioncurso = models.TextField(verbose_name='Descripción del Curso')
    
    # Entidad
    entidadpatrocinadora = models.CharField(max_length=100, verbose_name='Entidad Patrocinadora')
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, verbose_name='Nombre de Contacto')
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, verbose_name='Teléfono de Contacto')
    emailempresapatrocinadora = models.EmailField(max_length=60, blank=True, verbose_name='Email Patrocinador')
    
    # Control
    activarparaqueseveaenfront = models.BooleanField(default=True, verbose_name='Activar para Front')
    
    # Certificado
    rutacertificado = models.FileField(
        upload_to='certificados/cursos/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name='Certificado'
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cursosrealizados'
        verbose_name = 'Curso Realizado'
        verbose_name_plural = 'Cursos Realizados'
        ordering = ['-fechainicio']  # CORREGIDO: Orden cronológico
    
    def __str__(self):
        return f"{self.nombrecurso} - {self.entidadpatrocinadora}"
    
    def clean(self):
        # CORRIGE: Validación completa de fechas
        if self.fechafin:
            if self.fechafin > date.today():
                raise ValidationError({'fechafin': 'La fecha de finalización no puede ser futura'})
            
            if self.fechainicio and self.fechafin < self.fechainicio:
                raise ValidationError({'fechafin': 'La fecha de finalización no puede ser anterior a la fecha de inicio'})


# ======================================
# MODELO: PRODUCTOS ACADÉMICOS
# ======================================

class ProductoAcademico(models.Model):
    """
    Tabla de productos académicos
    Mapea: PRODUCTOSACADEMICOS
    """
    idproductoacademico = models.AutoField(primary_key=True, db_column='idproductoacademico')
    idperfilconqueestaactivo = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        related_name='productos_academicos',
        db_column='idperfilconqueestaactivo'
    )
    
    nombrerecurso = models.CharField(max_length=100, verbose_name='Nombre del Recurso')
    clasificador = models.TextField(
        verbose_name='Clasificador',
        help_text='Etiquetas separadas por comas. Ej: ingeniería,tecnologíainformación,basesdedatos,pregrado'
    )
    descripcion = models.TextField(verbose_name='Descripción')
    
    # Control
    activarparaqueseveaenfront = models.BooleanField(default=True, verbose_name='Activar para Front')
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'productosacademicos'
        verbose_name = 'Producto Académico'
        verbose_name_plural = 'Productos Académicos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombrerecurso
    
    def get_etiquetas(self):
        """Devuelve lista de etiquetas"""
        return [tag.strip() for tag in self.clasificador.split(',') if tag.strip()]


# ======================================
# MODELO: PRODUCTOS LABORALES
# ======================================

class ProductoLaboral(models.Model):
    """
    Tabla de productos laborales
    Mapea: PRODUCTOSLABORALES
    """
    idproductoslaborales = models.AutoField(primary_key=True, db_column='idproductoslaborales')
    idperfilconqueestaactivo = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        related_name='productos_laborales',
        db_column='idperfilconqueestaactivo'
    )
    
    nombreproducto = models.CharField(max_length=100, verbose_name='Nombre del Producto')
    fechaproducto = models.DateField(verbose_name='Fecha del Producto', validators=[validar_fecha_pasada])
    descripcion = models.TextField(verbose_name='Descripción')
    
    # Control
    activarparaqueseveaenfront = models.BooleanField(default=True, verbose_name='Activar para Front')
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'productoslaborales'
        verbose_name = 'Producto Laboral'
        verbose_name_plural = 'Productos Laborales'
        ordering = ['-fechaproducto']
    
    def __str__(self):
        return self.nombreproducto


# ======================================
# MODELO: VENTA GARAGE
# ======================================

class VentaGarage(models.Model):
    """
    Tabla de venta garage
    Mapea: VENTAGARAGE
    CORRIGE: Solo permite "Bueno" o "Regular", agrega fecha de publicación e imagen
    """
    ESTADO_CHOICES = [
        ('Bueno', 'Bueno'),
        ('Regular', 'Regular'),
    ]
    
    idventagarage = models.AutoField(primary_key=True, db_column='idventagarage')
    idperfilconqueestaactivo = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        related_name='ventas_garage',
        db_column='idperfilconqueestaactivo'
    )
    
    nombreproducto = models.CharField(max_length=100, verbose_name='Nombre del Producto')
    estadoproducto = models.CharField(max_length=40, choices=ESTADO_CHOICES, verbose_name='Estado del Producto')
    descripcion = models.TextField(verbose_name='Descripción')
    valordelbien = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Valor del Bien')
    
    # CORRIGE: Agrega fecha de publicación e imagen
    fecha_publicacion = models.DateField(default=date.today, verbose_name='Fecha de Publicación')
    imagen_producto = models.ImageField(
        upload_to='venta_garage/',
        blank=True,
        null=True,
        verbose_name='Imagen del Producto'
    )
    
    # Control
    activarparaqueseveaenfront = models.BooleanField(default=True, verbose_name='Activar para Front')
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ventagarage'
        verbose_name = 'Venta Garage'
        verbose_name_plural = 'Ventas Garage'
        ordering = ['-fecha_publicacion']
    
    def __str__(self):
        return f"{self.nombreproducto} - ${self.valordelbien}"
    
    def get_color_estado(self):
        """Devuelve color según estado (CORRIGE observación)"""
        if self.estadoproducto == 'Bueno':
            return '#28a745'  # Verde
        else:
            return '#ffc107'  # Amarillo
