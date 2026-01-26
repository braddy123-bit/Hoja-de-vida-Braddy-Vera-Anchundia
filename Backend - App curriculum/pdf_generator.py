

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import date


def generar_cv_pdf_profesional(perfil, secciones_seleccionadas=None):
    """
    Genera PDF con secciones seleccionables
    
    Args:
        perfil: Instancia de DatosPersonales
        secciones_seleccionadas: Dict con las secciones a incluir
            {
                'experiencia': True/False,
                'reconocimientos': True/False,
                'cursos': True/False,
                'productos_academicos': True/False,
                'productos_laborales': True/False,
                'venta_garage': True/False
            }
    """
    buffer = BytesIO()
    
    # Si no se especifican secciones, usar configuración del perfil
    if secciones_seleccionadas is None:
        secciones_seleccionadas = {
            'experiencia': perfil.mostrar_experiencia_pdf,
            'reconocimientos': perfil.mostrar_reconocimientos_pdf,
            'cursos': perfil.mostrar_cursos_pdf,
            'productos_academicos': perfil.mostrar_productos_academicos_pdf,
            'productos_laborales': perfil.mostrar_productos_laborales_pdf,
            'venta_garage': perfil.mostrar_venta_garage_pdf,
        }
    
    # Configuración del documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=f"CV_{perfil.nombre_completo}"
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitulo_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#666666'),
        spaceAfter=15,
        alignment=TA_CENTER
    )
    
    seccion_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    texto_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    texto_bold = ParagraphStyle(
        'CustomBold',
        parent=texto_normal,
        fontName='Helvetica-Bold'
    )
    
    # ======================================
    # ENCABEZADO
    # ======================================
    
    nombre = Paragraph(perfil.nombre_completo.upper(), titulo_style)
    elements.append(nombre)
    
    # Información básica
    info_basica = f"{perfil.descripcionperfil}"
    elements.append(Paragraph(info_basica, subtitulo_style))
    
    # Datos de contacto
    contacto_data = [
        [
            Paragraph(f"<b>Cédula:</b> {perfil.numerocedula}", texto_normal),
            Paragraph(f"<b>Edad:</b> {perfil.edad} años", texto_normal),
        ],
        [
            Paragraph(f"<b>Teléfono:</b> {perfil.telefonoconvencional or perfil.telefonofijo}", texto_normal),
            Paragraph(f"<b>Estado Civil:</b> {perfil.estadocivil}", texto_normal),
        ],
        [
            Paragraph(f"<b>Dirección:</b> {perfil.direcciondomiciliaria}", texto_normal),
            Paragraph(f"<b>Nacionalidad:</b> {perfil.nacionalidad}", texto_normal),
        ]
    ]
    
    if perfil.sitioweb:
        contacto_data.append([
            Paragraph(f"<b>Sitio Web:</b> {perfil.sitioweb}", texto_normal),
            Paragraph(f"<b>Licencia:</b> {perfil.get_licenciaconducir_display()}", texto_normal),
        ])
    
    contacto_table = Table(contacto_data, colWidths=[8*cm, 8*cm])
    contacto_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(contacto_table)
    elements.append(Spacer(1, 0.3*cm))
    
    # Línea separadora
    linea = Table([['']], colWidths=[16*cm])
    linea.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#2E7D32')),
    ]))
    elements.append(linea)
    elements.append(Spacer(1, 0.3*cm))
    
    # ======================================
    # EXPERIENCIA LABORAL
    # ======================================
    
    if secciones_seleccionadas.get('experiencia', False):
        experiencias = perfil.experiencias_laborales.filter(activarparaqueseveaenfront=True).order_by('-fechainiciogestion')
        
        if experiencias.exists():
            elements.append(Paragraph("EXPERIENCIA LABORAL", seccion_style))
            
            for exp in experiencias:
                exp_elementos = []
                
                cargo_empresa = Paragraph(
                    f"<b>{exp.cargodesempenado}</b> - {exp.nombrempresa}",
                    texto_bold
                )
                exp_elementos.append(cargo_empresa)
                
                fecha_inicio = exp.fechainiciogestion.strftime("%m/%Y")
                fecha_fin = exp.fechafingestion.strftime("%m/%Y") if exp.fechafingestion else "Presente"
                
                fechas = Paragraph(
                    f"{fecha_inicio} - {fecha_fin} | {exp.lugarempresa}",
                    ParagraphStyle('dates', parent=texto_normal, fontSize=9, textColor=colors.grey)
                )
                exp_elementos.append(fechas)
                
                if exp.descripcionfunciones:
                    desc = Paragraph(exp.descripcionfunciones, texto_normal)
                    exp_elementos.append(desc)
                
                exp_elementos.append(Spacer(1, 0.3*cm))
                
                elements.append(KeepTogether(exp_elementos))
    
    # ======================================
    # RECONOCIMIENTOS
    # ======================================
    
    if secciones_seleccionadas.get('reconocimientos', False):
        reconocimientos = perfil.reconocimientos.filter(activarparaqueseveaenfront=True).order_by('-fechareconocimiento')
        
        if reconocimientos.exists():
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph("RECONOCIMIENTOS", seccion_style))
            
            for rec in reconocimientos:
                rec_elementos = []
                
                titulo_rec = Paragraph(
                    f"<b>{rec.tiporeconocimiento}</b> - {rec.entidadpatrocinadora}",
                    texto_bold
                )
                rec_elementos.append(titulo_rec)
                
                fecha_rec = Paragraph(
                    f"{rec.fechareconocimiento.strftime('%m/%Y')}",
                    ParagraphStyle('dates', parent=texto_normal, fontSize=9, textColor=colors.grey)
                )
                rec_elementos.append(fecha_rec)
                
                if rec.descripcionreconocimiento:
                    desc_rec = Paragraph(rec.descripcionreconocimiento, texto_normal)
                    rec_elementos.append(desc_rec)
                
                rec_elementos.append(Spacer(1, 0.3*cm))
                
                elements.append(KeepTogether(rec_elementos))
    
    # ======================================
    # CURSOS REALIZADOS
    # ======================================
    
    if secciones_seleccionadas.get('cursos', False):
        cursos = perfil.cursos_realizados.filter(activarparaqueseveaenfront=True).order_by('-fechainicio')
        
        if cursos.exists():
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph("CURSOS REALIZADOS", seccion_style))
            
            for curso in cursos:
                curso_elementos = []
                
                titulo_curso = Paragraph(
                    f"<b>{curso.nombrecurso}</b> - {curso.entidadpatrocinadora}",
                    texto_bold
                )
                curso_elementos.append(titulo_curso)
                
                fecha_curso = Paragraph(
                    f"{curso.fechainicio.strftime('%m/%Y')} - {curso.fechafin.strftime('%m/%Y')} | {curso.totalhoras} horas",
                    ParagraphStyle('dates', parent=texto_normal, fontSize=9, textColor=colors.grey)
                )
                curso_elementos.append(fecha_curso)
                
                if curso.descripcioncurso:
                    desc_curso = Paragraph(curso.descripcioncurso, texto_normal)
                    curso_elementos.append(desc_curso)
                
                curso_elementos.append(Spacer(1, 0.3*cm))
                
                elements.append(KeepTogether(curso_elementos))
    
    # ======================================
    # PRODUCTOS ACADÉMICOS
    # ======================================
    
    if secciones_seleccionadas.get('productos_academicos', False):
        productos_acad = perfil.productos_academicos.filter(activarparaqueseveaenfront=True)
        
        if productos_acad.exists():
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph("PRODUCTOS ACADÉMICOS", seccion_style))
            
            for prod in productos_acad:
                prod_elementos = []
                
                titulo_prod = Paragraph(f"<b>{prod.nombrerecurso}</b>", texto_bold)
                prod_elementos.append(titulo_prod)
                
                if prod.clasificador:
                    etiquetas = Paragraph(
                        f"<i>Clasificadores: {prod.clasificador}</i>",
                        ParagraphStyle('tags', parent=texto_normal, fontSize=9, textColor=colors.grey)
                    )
                    prod_elementos.append(etiquetas)
                
                if prod.descripcion:
                    desc_prod = Paragraph(prod.descripcion, texto_normal)
                    prod_elementos.append(desc_prod)
                
                prod_elementos.append(Spacer(1, 0.3*cm))
                
                elements.append(KeepTogether(prod_elementos))
    
    # ======================================
    # PRODUCTOS LABORALES
    # ======================================
    
    if secciones_seleccionadas.get('productos_laborales', False):
        productos_lab = perfil.productos_laborales.filter(activarparaqueseveaenfront=True).order_by('-fechaproducto')
        
        if productos_lab.exists():
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph("PRODUCTOS LABORALES", seccion_style))
            
            for prod in productos_lab:
                prod_elementos = []
                
                titulo_prod = Paragraph(f"<b>{prod.nombreproducto}</b>", texto_bold)
                prod_elementos.append(titulo_prod)
                
                fecha_prod = Paragraph(
                    f"{prod.fechaproducto.strftime('%m/%Y')}",
                    ParagraphStyle('dates', parent=texto_normal, fontSize=9, textColor=colors.grey)
                )
                prod_elementos.append(fecha_prod)
                
                if prod.descripcion:
                    desc_prod = Paragraph(prod.descripcion, texto_normal)
                    prod_elementos.append(desc_prod)
                
                prod_elementos.append(Spacer(1, 0.3*cm))
                
                elements.append(KeepTogether(prod_elementos))
    
    # ======================================
    # VENTA GARAGE
    # ======================================
    
    if secciones_seleccionadas.get('venta_garage', False):
        ventas = perfil.ventas_garage.filter(activarparaqueseveaenfront=True).order_by('-fecha_publicacion')
        
        if ventas.exists():
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph("VENTA GARAGE", seccion_style))
            
            for venta in ventas:
                venta_elementos = []
                
                titulo_venta = Paragraph(
                    f"<b>{venta.nombreproducto}</b> - Estado: {venta.estadoproducto}",
                    texto_bold
                )
                venta_elementos.append(titulo_venta)
                
                precio = Paragraph(
                    f"Precio: ${venta.valordelbien} | Publicado: {venta.fecha_publicacion.strftime('%d/%m/%Y')}",
                    texto_normal
                )
                venta_elementos.append(precio)
                
                if venta.descripcion:
                    desc_venta = Paragraph(venta.descripcion, texto_normal)
                    venta_elementos.append(desc_venta)
                
                venta_elementos.append(Spacer(1, 0.3*cm))
                
                elements.append(KeepTogether(venta_elementos))
    
    # ======================================
    # PIE DE PÁGINA
    # ======================================
    
    elements.append(Spacer(1, 1*cm))
    
    pie = Paragraph(
        f"<i>CV generado el {date.today().strftime('%d/%m/%Y')}</i>",
        ParagraphStyle('footer', parent=texto_normal, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(pie)
    
    # ======================================
    # CONSTRUIR PDF
    # ======================================
    
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
