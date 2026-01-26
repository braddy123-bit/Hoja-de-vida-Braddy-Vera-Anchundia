

from django.contrib import admin
from django.utils.html import format_html
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
# INLINES
# ======================================

class ExperienciaLaboralInline(admin.TabularInline):
    model = ExperienciaLaboral
    extra = 0
    fields = ['cargodesempenado', 'nombrempresa', 'fechainiciogestion', 'fechafingestion', 'activarparaqueseveaenfront']
    readonly_fields = []


class ReconocimientoInline(admin.TabularInline):
    model = Reconocimiento
    extra = 0
    fields = ['tiporeconocimiento', 'fechareconocimiento', 'entidadpatrocinadora', 'activarparaqueseveaenfront']


class CursoRealizadoInline(admin.TabularInline):
    model = CursoRealizado
    extra = 0
    fields = ['nombrecurso', 'fechainicio', 'fechafin', 'entidadpatrocinadora', 'activarparaqueseveaenfront']


# ======================================
# ADMIN: DATOS PERSONALES
# ======================================

@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    list_display = [
        'foto_preview',
        'nombre_completo',
        'numerocedula',
        'edad',
        'perfilactivo_badge',
        'fecha_actualizacion'
    ]
    
    list_filter = ['perfilactivo', 'sexo', 'estadocivil', 'fecha_creacion']
    search_fields = ['nombres', 'apellidos', 'numerocedula']
    
    readonly_fields = ['slug', 'fecha_creacion', 'fecha_actualizacion', 'foto_preview_large', 'edad']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario', 'descripcionperfil', 'perfilactivo')
        }),
        ('Información Personal', {
            'fields': (
                'nombres',
                'apellidos',
                'fechanacimiento',
                'edad',
                'nacionalidad',
                'lugarnacimiento',
                'numerocedula',
                'sexo',
                'estadocivil',
                'licenciaconducir',
                'foto',
                'foto_preview_large'
            )
        }),
        ('Contacto', {
            'fields': (
                'telefonoconvencional',
                'telefonofijo',
                'direcciontrabajo',
                'direcciondomiciliaria',
                'sitioweb'
            )
        }),
        ('⚙️ CONTROL DE SECCIONES EN PDF', {
            'fields': (
                'mostrar_experiencia_pdf',
                'mostrar_reconocimientos_pdf',
                'mostrar_cursos_pdf',
                'mostrar_productos_academicos_pdf',
                'mostrar_productos_laborales_pdf',
                'mostrar_venta_garage_pdf'
            ),
            'classes': ('wide',),
            'description': 'Selecciona qué secciones se mostrarán en el PDF generado'
        }),
        ('Configuración', {
            'fields': ('slug',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ExperienciaLaboralInline, ReconocimientoInline, CursoRealizadoInline]
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />',
                obj.foto.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #ddd; border-radius: 50%;"></div>')
    
    foto_preview.short_description = 'Foto'
    
    def foto_preview_large(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" width="200" height="200" style="border-radius: 10px; object-fit: cover;" />',
                obj.foto.url
            )
        return 'Sin foto'
    
    foto_preview_large.short_description = 'Vista previa'
    
    def perfilactivo_badge(self, obj):
        if obj.perfilactivo:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Activo</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">✗ Inactivo</span>'
        )
    
    perfilactivo_badge.short_description = 'Estado'


# ======================================
# ADMIN: EXPERIENCIA LABORAL
# ======================================

@admin.register(ExperienciaLaboral)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    list_display = [
        'cargodesempenado',
        'nombrempresa',
        'fechainiciogestion',
        'fechafingestion',
        'activar_badge',
        'idperfilconqueestaactivo'
    ]
    
    list_filter = ['activarparaqueseveaenfront', 'fechainiciogestion']
    search_fields = ['cargodesempenado', 'nombrempresa']
    ordering = ['-fechainiciogestion']
    
    fieldsets = (
        ('Información del Cargo', {
            'fields': (
                'idperfilconqueestaactivo',
                'cargodesempenado',
                'nombrempresa',
                'lugarempresa'
            )
        }),
        ('Contacto Empresarial', {
            'fields': (
                'emailempresa',
                'sitiowebempresa',
                'nombrecontactoempresarial',
                'telefonocontactoempresarial'
            )
        }),
        ('Fechas y Funciones', {
            'fields': (
                'fechainiciogestion',
                'fechafingestion',
                'descripcionfunciones'
            )
        }),
        ('Certificado y Visibilidad', {
            'fields': (
                'rutacertificado',
                'activarparaqueseveaenfront'
            )
        }),
    )
    
    def activar_badge(self, obj):
        if obj.activarparaqueseveaenfront:
            return format_html('<span style="color: green;">✓ Visible</span>')
        return format_html('<span style="color: red;">✗ Oculto</span>')
    
    activar_badge.short_description = 'Visibilidad'


# ======================================
# ADMIN: RECONOCIMIENTOS
# ======================================

@admin.register(Reconocimiento)
class ReconocimientoAdmin(admin.ModelAdmin):
    list_display = [
        'tiporeconocimiento',
        'entidadpatrocinadora',
        'fechareconocimiento',
        'activar_badge',
        'idperfilconqueestaactivo'
    ]
    
    list_filter = ['tiporeconocimiento', 'activarparaqueseveaenfront', 'fechareconocimiento']
    search_fields = ['entidadpatrocinadora', 'descripcionreconocimiento']
    ordering = ['-fechareconocimiento']
    
    def activar_badge(self, obj):
        if obj.activarparaqueseveaenfront:
            return format_html('<span style="color: green;">✓ Visible</span>')
        return format_html('<span style="color: red;">✗ Oculto</span>')
    
    activar_badge.short_description = 'Visibilidad'


# ======================================
# ADMIN: CURSOS REALIZADOS
# ======================================

@admin.register(CursoRealizado)
class CursoRealizadoAdmin(admin.ModelAdmin):
    list_display = [
        'nombrecurso',
        'entidadpatrocinadora',
        'fechainicio',
        'fechafin',
        'totalhoras',
        'activar_badge',
        'idperfilconqueestaactivo'
    ]
    
    list_filter = ['activarparaqueseveaenfront', 'fechainicio']
    search_fields = ['nombrecurso', 'entidadpatrocinadora']
    ordering = ['-fechainicio']
    
    def activar_badge(self, obj):
        if obj.activarparaqueseveaenfront:
            return format_html('<span style="color: green;">✓ Visible</span>')
        return format_html('<span style="color: red;">✗ Oculto</span>')
    
    activar_badge.short_description = 'Visibilidad'


# ======================================
# ADMIN: PRODUCTOS ACADÉMICOS
# ======================================

@admin.register(ProductoAcademico)
class ProductoAcademicoAdmin(admin.ModelAdmin):
    list_display = [
        'nombrerecurso',
        'clasificador_preview',
        'activar_badge',
        'idperfilconqueestaactivo'
    ]
    
    list_filter = ['activarparaqueseveaenfront']
    search_fields = ['nombrerecurso', 'clasificador']
    
    def clasificador_preview(self, obj):
        tags = obj.get_etiquetas()[:3]
        return ', '.join(tags) + ('...' if len(obj.get_etiquetas()) > 3 else '')
    
    clasificador_preview.short_description = 'Etiquetas'
    
    def activar_badge(self, obj):
        if obj.activarparaqueseveaenfront:
            return format_html('<span style="color: green;">✓ Visible</span>')
        return format_html('<span style="color: red;">✗ Oculto</span>')
    
    activar_badge.short_description = 'Visibilidad'


# ======================================
# ADMIN: PRODUCTOS LABORALES
# ======================================

@admin.register(ProductoLaboral)
class ProductoLaboralAdmin(admin.ModelAdmin):
    list_display = [
        'nombreproducto',
        'fechaproducto',
        'activar_badge',
        'idperfilconqueestaactivo'
    ]
    
    list_filter = ['activarparaqueseveaenfront', 'fechaproducto']
    search_fields = ['nombreproducto']
    ordering = ['-fechaproducto']
    
    def activar_badge(self, obj):
        if obj.activarparaqueseveaenfront:
            return format_html('<span style="color: green;">✓ Visible</span>')
        return format_html('<span style="color: red;">✗ Oculto</span>')
    
    activar_badge.short_description = 'Visibilidad'


# ======================================
# ADMIN: VENTA GARAGE
# ======================================

@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    list_display = [
        'imagen_preview',
        'nombreproducto',
        'estado_badge',
        'valordelbien',
        'fecha_publicacion',
        'activar_badge',
        'idperfilconqueestaactivo'
    ]
    
    list_filter = ['estadoproducto', 'activarparaqueseveaenfront', 'fecha_publicacion']
    search_fields = ['nombreproducto']
    ordering = ['-fecha_publicacion']
    
    readonly_fields = ['imagen_preview_large']
    
    fieldsets = (
        ('Información del Producto', {
            'fields': (
                'idperfilconqueestaactivo',
                'nombreproducto',
                'estadoproducto',
                'descripcion',
                'valordelbien'
            )
        }),
        ('Publicación e Imagen', {
            'fields': (
                'fecha_publicacion',
                'imagen_producto',
                'imagen_preview_large'
            )
        }),
        ('Visibilidad', {
            'fields': ('activarparaqueseveaenfront',)
        }),
    )
    
    def imagen_preview(self, obj):
        if obj.imagen_producto:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius: 5px; object-fit: cover;" />',
                obj.imagen_producto.url
            )
        return '📦'
    
    imagen_preview.short_description = 'Imagen'
    
    def imagen_preview_large(self, obj):
        if obj.imagen_producto:
            return format_html(
                '<img src="{}" width="300" height="300" style="border-radius: 10px; object-fit: cover;" />',
                obj.imagen_producto.url
            )
        return 'Sin imagen'
    
    imagen_preview_large.short_description = 'Vista previa'
    
    def estado_badge(self, obj):
        color = obj.get_color_estado()
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.estadoproducto
        )
    
    estado_badge.short_description = 'Estado'
    
    def activar_badge(self, obj):
        if obj.activarparaqueseveaenfront:
            return format_html('<span style="color: green;">✓ Visible</span>')
        return format_html('<span style="color: red;">✗ Oculto</span>')
    
    activar_badge.short_description = 'Visibilidad'
