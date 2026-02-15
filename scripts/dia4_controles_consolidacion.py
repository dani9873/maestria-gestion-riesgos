#!/usr/bin/env python3
"""
DÍA 4: Selección de Controles y Consolidación del Proyecto
Basado en ISO/IEC 27001:2022 Anexo A
"""

import json
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# Configuración
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

class GestorControles:
    """Clase para gestionar controles ISO 27001"""
    
    def __init__(self, archivo_controles, archivo_riesgos):
        self.controles = self.cargar_json(archivo_controles, 'controles')
        self.riesgos = self.cargar_csv_riesgos(archivo_riesgos)
        self.asignaciones = []
    
    def cargar_json(self, archivo, clave):
        """Cargar datos desde JSON"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data[clave]
        except Exception as e:
            print(f"✗ Error cargando {archivo}: {e}")
            return []
    
    def cargar_csv_riesgos(self, archivo):
        """Cargar matriz de riesgos desde CSV"""
        try:
            df = pd.read_csv(archivo, encoding='utf-8')
            return df
        except Exception as e:
            print(f"✗ Error cargando riesgos: {e}")
            return pd.DataFrame()
    
    def relacionar_controles_riesgos(self):
        """
        Relacionar controles con riesgos específicos
        basándose en las amenazas identificadas
        """
        print("\n" + "="*70)
        print("ASIGNACIÓN AUTOMÁTICA DE CONTROLES A RIESGOS")
        print("="*70)
        
        if self.riesgos.empty:
            print("✗ No hay riesgos para procesar")
            return None
        
        # Filtrar solo riesgos que requieren control
        riesgos_criticos = self.riesgos[self.riesgos['requiere_control'] == True].copy()
        
        print(f"\n🔍 Procesando {len(riesgos_criticos)} riesgos que requieren controles...")
        
        for idx, riesgo in riesgos_criticos.iterrows():
            amenaza = riesgo['amenaza_nombre']
            
            # Buscar controles aplicables
            controles_aplicables = [
                control for control in self.controles
                if amenaza in control.get('aplicable_a', [])
            ]
            
            for control in controles_aplicables:
                asignacion = {
                    'id_riesgo': riesgo['id_riesgo'],
                    'activo': riesgo['activo_nombre'],
                    'amenaza': riesgo['amenaza_nombre'],
                    'nivel_riesgo': riesgo['nivel_riesgo'],
                    'clasificacion': riesgo['clasificacion'],
                    'control_id': control['id'],
                    'control_nombre': control['nombre'],
                    'control_categoria': control['categoria'],
                    'control_tipo': control['tipo_control']
                }
                self.asignaciones.append(asignacion)
        
        print(f"✓ Total de asignaciones control-riesgo: {len(self.asignaciones)}")
        
        # Estadísticas
        df_asig = pd.DataFrame(self.asignaciones)
        print(f"\n📊 Controles por categoría:")
        print(df_asig['control_categoria'].value_counts())
        
        print(f"\n📊 Controles por tipo:")
        print(df_asig['control_tipo'].value_counts())
        
        return df_asig
    
    def generar_declaracion_aplicabilidad(self, df_asig, archivo_salida):
        """Generar Declaración de Aplicabilidad (Statement of Applicability)"""
        print("\n" + "="*70)
        print("GENERANDO DECLARACIÓN DE APLICABILIDAD (SoA)")
        print("="*70)
        
        if df_asig is None or df_asig.empty:
            print("✗ No hay asignaciones para generar SoA")
            return False
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("DECLARACIÓN DE APLICABILIDAD (SoA)\n")
            f.write("Statement of Applicability - ISO/IEC 27001:2022\n")
            f.write("="*80 + "\n\n")
            f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Organización: [Nombre de la Organización]\n")
            f.write(f"Alcance: Gestión de Riesgos de Seguridad de la Información\n\n")
            
            # Controles únicos aplicables
            controles_unicos = df_asig.groupby(['control_id', 'control_nombre', 
                                                'control_categoria']).size().reset_index(name='frecuencia')
            controles_unicos = controles_unicos.sort_values(['control_categoria', 'control_id'])
            
            f.write(f"Total de controles aplicables: {len(controles_unicos)}\n\n")
            
            # Agrupar por categoría
            for categoria in controles_unicos['control_categoria'].unique():
                f.write(f"\n{'='*80}\n")
                f.write(f"CATEGORÍA: {categoria.upper()}\n")
                f.write(f"{'='*80}\n\n")
                
                controles_cat = controles_unicos[controles_unicos['control_categoria'] == categoria]
                
                for idx, control in controles_cat.iterrows():
                    f.write(f"Control: {control['control_id']} - {control['control_nombre']}\n")
                    f.write(f"{'-'*80}\n")
                    f.write(f"Aplicabilidad: SÍ\n")
                    f.write(f"Frecuencia de uso: {control['frecuencia']} riesgo(s)\n")
                    
                    # Buscar justificación
                    riesgos_control = df_asig[df_asig['control_id'] == control['control_id']]
                    amenazas = riesgos_control['amenaza'].unique()
                    
                    f.write(f"Justificación: Necesario para mitigar:\n")
                    for amenaza in amenazas[:3]:  # Máximo 3 ejemplos
                        f.write(f"  - {amenaza}\n")
                    
                    f.write(f"Estado de implementación: [PENDIENTE/EN PROCESO/IMPLEMENTADO]\n")
                    f.write(f"Responsable: [A definir]\n")
                    f.write(f"Fecha objetivo: [A definir]\n\n")
        
        print(f"✓ Declaración de Aplicabilidad generada: {archivo_salida}")
        
        # También generar versión CSV
        archivo_csv = archivo_salida.replace('.txt', '_resumen.csv')
        controles_unicos.to_csv(archivo_csv, index=False, encoding='utf-8')
        print(f"✓ Resumen en CSV: {archivo_csv}")
        
        return True
    
    def exportar_asignaciones(self, df_asig, archivo_salida):
        """Exportar todas las asignaciones control-riesgo"""
        if df_asig is None or df_asig.empty:
            return False
        
        df_asig.to_csv(archivo_salida, index=False, encoding='utf-8')
        print(f"✓ Asignaciones exportadas: {archivo_salida}")
        return True
    
    def generar_graficos(self, df_asig, directorio_salida):
        """Generar visualizaciones de controles"""
        if df_asig is None or df_asig.empty:
            print("✗ No hay datos para graficar")
            return
        
        print("\n" + "="*70)
        print("GENERANDO GRÁFICOS DE CONTROLES")
        print("="*70)
        
        # Gráfico 1: Controles por categoría
        plt.figure(figsize=(10, 6))
        cat_counts = df_asig['control_categoria'].value_counts()
        colors_cat = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        
        plt.pie(cat_counts.values, labels=cat_counts.index, autopct='%1.1f%%',
               colors=colors_cat, startangle=90)
        plt.title('Distribución de Controles por Categoría', 
                 fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        archivo1 = os.path.join(directorio_salida, 'controles_por_categoria.png')
        plt.savefig(archivo1, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo1}")
        plt.close()
        
        # Gráfico 2: Controles por tipo
        plt.figure(figsize=(10, 6))
        tipo_counts = df_asig['control_tipo'].value_counts()
        colors_tipo = ['green', 'orange', 'blue', 'red']
        
        plt.bar(tipo_counts.index, tipo_counts.values, color=colors_tipo, edgecolor='black')
        plt.xlabel('Tipo de Control', fontsize=12, fontweight='bold')
        plt.ylabel('Cantidad', fontsize=12, fontweight='bold')
        plt.title('Distribución de Controles por Tipo', 
                 fontsize=14, fontweight='bold')
        plt.xticks(rotation=15)
        
        for i, v in enumerate(tipo_counts.values):
            plt.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        
        plt.tight_layout()
        archivo2 = os.path.join(directorio_salida, 'controles_por_tipo.png')
        plt.savefig(archivo2, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo2}")
        plt.close()
        
        # Gráfico 3: Top 10 controles más utilizados
        plt.figure(figsize=(12, 8))
        top_controles = df_asig.groupby(['control_id', 'control_nombre']).size().reset_index(name='count')
        top_controles = top_controles.sort_values('count', ascending=False).head(10)
        
        plt.barh(range(len(top_controles)), top_controles['count'], color='steelblue', edgecolor='black')
        plt.yticks(range(len(top_controles)), 
                  [f"{row['control_id']}: {row['control_nombre'][:40]}" 
                   for _, row in top_controles.iterrows()],
                  fontsize=9)
        plt.xlabel('Número de Riesgos Mitigados', fontsize=12, fontweight='bold')
        plt.title('Top 10 Controles Más Utilizados', fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        
        plt.tight_layout()
        archivo3 = os.path.join(directorio_salida, 'top10_controles.png')
        plt.savefig(archivo3, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo3}")
        plt.close()
        
        # Gráfico 4: Cobertura de riesgos críticos
        plt.figure(figsize=(12, 6))
        
        # Riesgos por clasificación
        riesgos_clasificacion = self.riesgos[self.riesgos['requiere_control'] == True]['clasificacion'].value_counts()
        
        # Riesgos con control asignado
        riesgos_con_control = df_asig['clasificacion'].value_counts()
        
        x = range(len(riesgos_clasificacion))
        width = 0.35
        
        plt.bar([i - width/2 for i in x], riesgos_clasificacion.values, 
               width, label='Riesgos Totales', color='coral', edgecolor='black')
        plt.bar([i + width/2 for i in x], 
               [riesgos_con_control.get(cat, 0) for cat in riesgos_clasificacion.index], 
               width, label='Con Control Asignado', color='lightgreen', edgecolor='black')
        
        plt.xlabel('Clasificación de Riesgo', fontsize=12, fontweight='bold')
        plt.ylabel('Cantidad', fontsize=12, fontweight='bold')
        plt.title('Cobertura de Controles por Clasificación de Riesgo', 
                 fontsize=14, fontweight='bold')
        plt.xticks(x, riesgos_clasificacion.index)
        plt.legend()
        
        plt.tight_layout()
        archivo4 = os.path.join(directorio_salida, 'cobertura_controles.png')
        plt.savefig(archivo4, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo4}")
        plt.close()


class GeneradorReportePDF:
    """Clase para generar reporte final consolidado en PDF"""
    
    def __init__(self, dir_base):
        self.dir_base = dir_base
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Estilo personalizado para título
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12
        ))
    
    def agregar_portada(self):
        """Agregar portada al reporte"""
        self.story.append(Spacer(1, 2*inch))
        
        titulo = Paragraph(
            "REPORTE CONSOLIDADO<br/>GESTIÓN DE RIESGOS<br/>Seguridad de la Información y Continuidad del Negocio",
            self.styles['CustomTitle']
        )
        self.story.append(titulo)
        self.story.append(Spacer(1, 0.5*inch))
        
        subtitulo = Paragraph(
            f"Basado en ISO/IEC 27005:2022, ISO 27001:2022 e ISO 31000:2018",
            self.styles['Normal']
        )
        self.story.append(subtitulo)
        self.story.append(Spacer(1, 0.3*inch))
        
        fecha = Paragraph(
            f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d')}",
            self.styles['Normal']
        )
        self.story.append(fecha)
        
        self.story.append(PageBreak())
    
    def agregar_resumen_ejecutivo(self):
        """Agregar resumen ejecutivo"""
        titulo = Paragraph("1. RESUMEN EJECUTIVO", self.styles['CustomHeading'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 12))
        
        # Cargar datos
        try:
            df_amenazas = pd.read_csv(os.path.join(self.dir_base, 'resultados/dia1/amenazas_identificadas.csv'))
            df_activos = pd.read_csv(os.path.join(self.dir_base, 'resultados/dia2/matriz_valoracion_activos.csv'))
            df_riesgos = pd.read_csv(os.path.join(self.dir_base, 'resultados/dia3/matriz_analisis_riesgos.csv'))
            df_controles = pd.read_csv(os.path.join(self.dir_base, 'resultados/dia4/asignaciones_control_riesgo.csv'))
            
            texto = f"""
            Este documento presenta el análisis integral de gestión de riesgos de seguridad de la información
            y continuidad del negocio, realizado siguiendo las directrices de ISO/IEC 27005:2022 e ISO 31000:2018.
            <br/><br/>
            <b>Resultados Principales:</b><br/>
            • Amenazas identificadas: {len(df_amenazas)}<br/>
            • Activos inventariados: {len(df_activos)}<br/>
            • Riesgos analizados: {len(df_riesgos)}<br/>
            • Riesgos críticos/altos: {len(df_riesgos[df_riesgos['clasificacion'].isin(['Crítico', 'Alto'])])}<br/>
            • Controles ISO 27001 asignados: {df_controles['control_id'].nunique()}<br/>
            <br/>
            La metodología aplicada integra la identificación de amenazas, valoración de activos según la triada CIA,
            análisis cuantitativo de riesgos y selección de controles del Anexo A de ISO 27001:2022.
            """
            
            parrafo = Paragraph(texto, self.styles['Normal'])
            self.story.append(parrafo)
            
        except Exception as e:
            texto = f"Error al cargar datos del resumen: {e}"
            self.story.append(Paragraph(texto, self.styles['Normal']))
        
        self.story.append(Spacer(1, 20))
    
    def agregar_seccion_amenazas(self):
        """Agregar sección de amenazas"""
        titulo = Paragraph("2. AMENAZAS IDENTIFICADAS", self.styles['CustomHeading'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 12))
        
        try:
            df = pd.read_csv(os.path.join(self.dir_base, 'resultados/dia1/amenazas_identificadas.csv'))
            
            texto = f"""
            Se identificaron {len(df)} amenazas potenciales clasificadas según su origen y naturaleza.
            La distribución incluye amenazas humanas (maliciosas y no intencionales), tecnológicas,
            ambientales y naturales.
            """
            self.story.append(Paragraph(texto, self.styles['Normal']))
            self.story.append(Spacer(1, 12))
            
            # Tabla resumen
            data = [['ID', 'Amenaza', 'Tipo', 'Probabilidad']]
            for _, row in df.head(10).iterrows():
                data.append([row['id'], row['nombre'][:30], row['tipo'][:20], str(row['probabilidad'])])
            
            tabla = Table(data)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            self.story.append(tabla)
            
        except Exception as e:
            self.story.append(Paragraph(f"Error: {e}", self.styles['Normal']))
        
        self.story.append(Spacer(1, 20))
    
    def agregar_seccion_activos(self):
        """Agregar sección de activos"""
        titulo = Paragraph("3. INVENTARIO Y VALORACIÓN DE ACTIVOS", self.styles['CustomHeading'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 12))
        
        try:
            df = pd.read_csv(os.path.join(self.dir_base, 'resultados/dia2/matriz_valoracion_activos.csv'))
            
            texto = f"""
            Se inventariaron {len(df)} activos críticos valorados según la triada CIA
            (Confidencialidad, Integridad, Disponibilidad). La valoración permite priorizar
            los esfuerzos de protección según su criticidad para la organización.
            """
            self.story.append(Paragraph(texto, self.styles['Normal']))
            self.story.append(Spacer(1, 12))
            
            # Top 5 activos críticos
            df_top = df.nlargest(5, 'valor_cia_ponderado')
            
            data = [['ID', 'Activo', 'Tipo', 'Valor CIA', 'Criticidad']]
            for _, row in df_top.iterrows():
                data.append([
                    row['id'], 
                    row['nombre'][:25], 
                    row['tipo'][:15],
                    f"{row['valor_cia_ponderado']:.1f}%",
                    row['criticidad']
                ])
            
            tabla = Table(data)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            self.story.append(tabla)
            
        except Exception as e:
            self.story.append(Paragraph(f"Error: {e}", self.styles['Normal']))
        
        self.story.append(Spacer(1, 20))
    
    def agregar_seccion_riesgos(self):
        """Agregar sección de análisis de riesgos"""
        titulo = Paragraph("4. ANÁLISIS DE RIESGOS", self.styles['CustomHeading'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 12))
        
        try:
            df = pd.read_csv(os.path.join(self.dir_base, 'resultados/dia3/matriz_analisis_riesgos.csv'))
            
            criticos = len(df[df['clasificacion'] == 'Crítico'])
            altos = len(df[df['clasificacion'] == 'Alto'])
            medios = len(df[df['clasificacion'] == 'Medio'])
            bajos = len(df[df['clasificacion'] == 'Bajo'])
            
            texto = f"""
            Se analizaron {len(df)} escenarios de riesgo aplicando la fórmula:
            Riesgo = Probabilidad × Impacto × Valor CIA del Activo.
            <br/><br/>
            <b>Distribución de riesgos:</b><br/>
            • Críticos: {criticos}<br/>
            • Altos: {altos}<br/>
            • Medios: {medios}<br/>
            • Bajos: {bajos}<br/>
            """
            self.story.append(Paragraph(texto, self.styles['Normal']))
            self.story.append(Spacer(1, 12))
            
            # Top 10 riesgos críticos
            df_top = df.nlargest(10, 'nivel_riesgo')
            
            data = [['ID', 'Activo', 'Amenaza', 'Nivel', 'Clasificación']]
            for _, row in df_top.iterrows():
                data.append([
                    row['id_riesgo'],
                    row['activo_nombre'][:20],
                    row['amenaza_nombre'][:25],
                    str(int(row['nivel_riesgo'])),
                    row['clasificacion']
                ])
            
            tabla = Table(data, colWidths=[0.8*inch, 1.5*inch, 1.8*inch, 0.7*inch, 0.9*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            self.story.append(tabla)
            
        except Exception as e:
            self.story.append(Paragraph(f"Error: {e}", self.styles['Normal']))
        
        self.story.append(Spacer(1, 20))
    
    def agregar_seccion_controles(self):
        """Agregar sección de controles"""
        titulo = Paragraph("5. CONTROLES ISO 27001 SELECCIONADOS", self.styles['CustomHeading'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 12))
        
        try:
            df = pd.read_csv(os.path.join(self.dir_base, 'resultados/dia4/asignaciones_control_riesgo.csv'))
            
            controles_unicos = df['control_id'].nunique()
            
            texto = f"""
            Se seleccionaron {controles_unicos} controles del Anexo A de ISO/IEC 27001:2022
            basándose en el análisis de riesgos. Los controles cubren las cuatro categorías:
            Organizacionales, de Personas, Físicos y Tecnológicos.
            """
            self.story.append(Paragraph(texto, self.styles['Normal']))
            self.story.append(Spacer(1, 12))
            
            # Top controles más utilizados
            top_controles = df.groupby(['control_id', 'control_nombre']).size().reset_index(name='frecuencia')
            top_controles = top_controles.sort_values('frecuencia', ascending=False).head(10)
            
            data = [['Control ID', 'Nombre del Control', 'Uso']]
            for _, row in top_controles.iterrows():
                data.append([
                    row['control_id'],
                    row['control_nombre'][:40],
                    str(row['frecuencia'])
                ])
            
            tabla = Table(data, colWidths=[1*inch, 3.5*inch, 0.7*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            self.story.append(tabla)
            
        except Exception as e:
            self.story.append(Paragraph(f"Error: {e}", self.styles['Normal']))
        
        self.story.append(Spacer(1, 20))
    
    def agregar_conclusiones(self):
        """Agregar conclusiones"""
        titulo = Paragraph("6. CONCLUSIONES Y RECOMENDACIONES", self.styles['CustomHeading'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 12))
        
        texto = """
        <b>Conclusiones principales:</b><br/><br/>
        
        1. <b>Identificación de Amenazas:</b> Se identificaron amenazas diversas que requieren
        un enfoque multicapa de seguridad, combinando controles preventivos, detectivos y correctivos.<br/><br/>
        
        2. <b>Valoración de Activos:</b> Los activos críticos identificados requieren protección
        prioritaria debido a su alto valor para la organización y su nivel de exposición.<br/><br/>
        
        3. <b>Análisis de Riesgos:</b> El análisis cuantitativo permitió priorizar eficazmente
        los esfuerzos de mitigación, enfocándose en los riesgos de mayor nivel.<br/><br/>
        
        4. <b>Selección de Controles:</b> Los controles seleccionados del Anexo A de ISO 27001
        proporcionan cobertura adecuada para los riesgos identificados.<br/><br/>
        
        <b>Recomendaciones:</b><br/><br/>
        
        • Implementar un programa de concienciación en seguridad para mitigar errores humanos<br/>
        • Establecer monitoreo continuo de amenazas y vulnerabilidades<br/>
        • Desarrollar un plan de continuidad del negocio basado en ISO 22301<br/>
        • Realizar revisiones periódicas del análisis de riesgos (al menos anualmente)<br/>
        • Implementar controles en orden de prioridad según el nivel de riesgo<br/>
        • Definir indicadores (KPIs) para medir la efectividad de los controles<br/>
        """
        
        self.story.append(Paragraph(texto, self.styles['Normal']))
        self.story.append(Spacer(1, 20))
    
    def generar_pdf(self, archivo_salida):
        """Generar el PDF completo"""
        print("\n" + "="*70)
        print("GENERANDO REPORTE PDF CONSOLIDADO")
        print("="*70)
        
        try:
            doc = SimpleDocTemplate(archivo_salida, pagesize=letter)
            
            # Construir contenido
            self.agregar_portada()
            self.agregar_resumen_ejecutivo()
            self.agregar_seccion_amenazas()
            self.agregar_seccion_activos()
            self.agregar_seccion_riesgos()
            self.agregar_seccion_controles()
            self.agregar_conclusiones()
            
            # Generar PDF
            doc.build(self.story)
            print(f"✓ Reporte PDF generado exitosamente: {archivo_salida}")
            return True
            
        except Exception as e:
            print(f"✗ Error generando PDF: {e}")
            return False


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("DÍA 4: SELECCIÓN DE CONTROLES Y CONSOLIDACIÓN DEL PROYECTO")
    print("Basado en ISO/IEC 27001:2022 Anexo A")
    print("="*70)
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Directorios
    dir_base = os.path.expanduser("~/maestria_gestion_riesgos")
    dir_resultados = os.path.join(dir_base, "resultados/dia4")
    dir_graficos = os.path.join(dir_base, "reportes/graficos")
    dir_pdf = os.path.join(dir_base, "reportes/pdf")
    
    os.makedirs(dir_resultados, exist_ok=True)
    os.makedirs(dir_graficos, exist_ok=True)
    os.makedirs(dir_pdf, exist_ok=True)
    
    # Archivos de entrada
    archivo_controles = os.path.join(dir_base, "data/controles_iso27001.json")
    archivo_riesgos = os.path.join(dir_base, "resultados/dia3/matriz_analisis_riesgos.csv")
    
    # PARTE 1: Gestión de Controles
    print("\n" + "-"*70)
    print("PARTE 1: ASIGNACIÓN DE CONTROLES")
    print("-"*70)
    
    gestor = GestorControles(archivo_controles, archivo_riesgos)
    
    # Relacionar controles con riesgos
    df_asignaciones = gestor.relacionar_controles_riesgos()
    
    if df_asignaciones is not None and not df_asignaciones.empty:
        # Exportar asignaciones
        archivo_asig = os.path.join(dir_resultados, "asignaciones_control_riesgo.csv")
        gestor.exportar_asignaciones(df_asignaciones, archivo_asig)
        
        # Generar Declaración de Aplicabilidad
        archivo_soa = os.path.join(dir_resultados, "declaracion_aplicabilidad.txt")
        gestor.generar_declaracion_aplicabilidad(df_asignaciones, archivo_soa)
        
        # Generar gráficos
        gestor.generar_graficos(df_asignaciones, dir_graficos)
    
    # PARTE 2: Reporte Consolidado PDF
    print("\n" + "-"*70)
    print("PARTE 2: GENERACIÓN DE REPORTE CONSOLIDADO")
    print("-"*70)
    
    generador_pdf = GeneradorReportePDF(dir_base)
    archivo_pdf = os.path.join(dir_pdf, "reporte_consolidado_gestion_riesgos.pdf")
    generador_pdf.generar_pdf(archivo_pdf)
    
    # RESUMEN FINAL
    print("\n" + "="*70)
    print("RESUMEN DEL DÍA 4")
    print("="*70)
    print(f"✓ Controles ISO 27001 relacionados con riesgos")
    print(f"✓ Declaración de Aplicabilidad (SoA) generada")
    print(f"✓ Asignaciones control-riesgo exportadas")
    print(f"✓ Gráficos de controles generados")
    print(f"✓ Reporte PDF consolidado creado")
    print(f"✓ Archivos en: {dir_resultados}")
    print(f"✓ PDF en: {dir_pdf}")
    print("\n" + "="*70)
    print("🎓 PROYECTO COMPLETADO EXITOSAMENTE")
    print("="*70)
    print("\n📝 Próximos pasos:")
    print("   1. Revisar reporte consolidado en PDF")
    print("   2. Elaborar documento académico de maestría")
    print("   3. Preparar presentación con hallazgos")
    print("   4. Documentar lecciones aprendidas")
    print("="*70)

if __name__ == "__main__":
    main()
