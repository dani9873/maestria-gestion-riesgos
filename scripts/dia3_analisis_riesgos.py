#!/usr/bin/env python3
"""
DÍA 3: Análisis de Riesgos y Generación de Requerimientos
Basado en ISO/IEC 27005 e ISO 31000
"""

import json
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuración
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

class AnalizadorRiesgos:
    """Clase para análisis y evaluación de riesgos"""
    
    def __init__(self, archivo_activos, archivo_amenazas):
        self.activos = self.cargar_json(archivo_activos, 'activos')
        self.amenazas = self.cargar_json(archivo_amenazas, 'amenazas')
        self.riesgos = []
        
        # Umbrales de riesgo
        self.umbrales = {
            'bajo': 5,
            'medio': 10,
            'alto': 15,
            'critico': 20
        }
        
        # Valores CIA
        self.valores_cia = {'bajo': 1, 'medio': 2, 'alto': 3}
    
    def cargar_json(self, archivo, clave):
        """Cargar datos desde archivo JSON"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data[clave]
        except Exception as e:
            print(f"✗ Error cargando {archivo}: {e}")
            return []
    
    def calcular_valor_cia(self, activo):
        """Calcular valor CIA total"""
        c = self.valores_cia.get(activo.get('confidencialidad', 'bajo'), 1)
        i = self.valores_cia.get(activo.get('integridad', 'bajo'), 1)
        a = self.valores_cia.get(activo.get('disponibilidad', 'bajo'), 1)
        return c + i + a
    
    def analizar_riesgos(self):
        """
        Realizar análisis de riesgos relacionando amenazas con activos
        Riesgo = Probabilidad × Impacto × Valor CIA del Activo
        """
        print("\n" + "="*70)
        print("ANÁLISIS DE RIESGOS")
        print("="*70)
        
        self.riesgos = []
        contador = 1
        
        # Relacionar cada amenaza con cada activo
        for amenaza in self.amenazas:
            for activo in self.activos:
                # Calcular componentes del riesgo
                probabilidad = amenaza.get('probabilidad', 3)
                
                # Impacto basado en el tipo de amenaza y activo
                impacto = self.calcular_impacto(amenaza, activo)
                
                # Valor CIA del activo
                valor_cia = self.calcular_valor_cia(activo)
                
                # Cálculo del riesgo
                nivel_riesgo = probabilidad * impacto * valor_cia
                
                # Clasificar riesgo
                clasificacion = self.clasificar_riesgo(nivel_riesgo)
                
                # Crear registro de riesgo
                riesgo = {
                    'id_riesgo': f"R{contador:03d}",
                    'activo_id': activo['id'],
                    'activo_nombre': activo['nombre'],
                    'amenaza_id': amenaza['id'],
                    'amenaza_nombre': amenaza['nombre'],
                    'probabilidad': probabilidad,
                    'impacto': impacto,
                    'valor_cia': valor_cia,
                    'nivel_riesgo': nivel_riesgo,
                    'clasificacion': clasificacion,
                    'requiere_control': nivel_riesgo > self.umbrales['medio']
                }
                
                self.riesgos.append(riesgo)
                contador += 1
        
        print(f"\n✓ Total de riesgos identificados: {len(self.riesgos)}")
        
        # Estadísticas
        df = pd.DataFrame(self.riesgos)
        print(f"\n📊 Distribución de riesgos por clasificación:")
        print(df['clasificacion'].value_counts())
        
        print(f"\n🚨 Riesgos que requieren controles: {df['requiere_control'].sum()}")
        
        # Top 10 riesgos más críticos
        print(f"\n🔴 Top 10 Riesgos Más Críticos:")
        top_riesgos = df.nlargest(10, 'nivel_riesgo')[
            ['id_riesgo', 'activo_nombre', 'amenaza_nombre', 'nivel_riesgo', 'clasificacion']
        ]
        for idx, row in top_riesgos.iterrows():
            print(f"   {row['id_riesgo']}: {row['amenaza_nombre']} → {row['activo_nombre']}")
            print(f"       Nivel: {row['nivel_riesgo']} ({row['clasificacion']})")
        
        return df
    
    def calcular_impacto(self, amenaza, activo):
        """
        Calcular impacto de una amenaza sobre un activo
        Considera tipo de amenaza y criticidad del activo
        """
        # Impacto base según tipo de amenaza
        impactos_base = {
            'Humana - Maliciosa': 4,
            'Tecnológica': 3,
            'Humana - No Intencional': 2,
            'Ambiental': 3,
            'Natural': 5
        }
        
        impacto_base = impactos_base.get(amenaza.get('tipo', ''), 3)
        
        # Ajustar según criticidad del activo
        criticidad_activo = activo.get('criticidad', 'medio')
        ajustes = {'bajo': 0.5, 'medio': 1.0, 'alto': 1.5, 'critico': 2.0}
        
        impacto_final = int(impacto_base * ajustes.get(criticidad_activo, 1.0))
        return min(impacto_final, 5)  # Máximo 5
    
    def clasificar_riesgo(self, nivel_riesgo):
        """Clasificar nivel de riesgo según umbrales"""
        if nivel_riesgo < self.umbrales['bajo']:
            return 'Bajo'
        elif nivel_riesgo < self.umbrales['medio']:
            return 'Medio'
        elif nivel_riesgo < self.umbrales['alto']:
            return 'Alto'
        else:
            return 'Crítico'
    
    def generar_matriz_riesgos(self, df, archivo_salida):
        """Generar matriz de riesgos en CSV"""
        if df is None or df.empty:
            print("✗ No hay riesgos para exportar")
            return False
        
        print("\n" + "="*70)
        print("GENERANDO MATRIZ DE RIESGOS")
        print("="*70)
        
        # Ordenar por nivel de riesgo descendente
        df_sorted = df.sort_values('nivel_riesgo', ascending=False)
        
        # Exportar
        df_sorted.to_csv(archivo_salida, index=False, encoding='utf-8')
        print(f"✓ Matriz de riesgos exportada: {archivo_salida}")
        
        return True
    
    def generar_requerimientos(self, df, archivo_salida):
        """
        Generar documento de requerimientos para riesgos que superan umbral
        """
        print("\n" + "="*70)
        print("GENERACIÓN DE REQUERIMIENTOS DE SEGURIDAD")
        print("="*70)
        
        # Filtrar riesgos que requieren control
        df_requieren_control = df[df['requiere_control'] == True].copy()
        
        if df_requieren_control.empty:
            print("✓ No hay riesgos que requieran controles adicionales")
            return False
        
        print(f"\n🔒 Total de requerimientos generados: {len(df_requieren_control)}")
        
        # Generar documento de texto
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("DOCUMENTO DE REQUERIMIENTOS DE SEGURIDAD\n")
            f.write("Basado en ISO/IEC 27005 y ISO 27001\n")
            f.write("="*80 + "\n\n")
            f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de requerimientos: {len(df_requieren_control)}\n\n")
            
            # Agrupar por clasificación
            for clasificacion in ['Crítico', 'Alto', 'Medio']:
                riesgos_clase = df_requieren_control[
                    df_requieren_control['clasificacion'] == clasificacion
                ]
                
                if not riesgos_clase.empty:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"RIESGOS {clasificacion.upper()}S\n")
                    f.write(f"{'='*80}\n\n")
                    
                    for idx, riesgo in riesgos_clase.iterrows():
                        f.write(f"REQUERIMIENTO {riesgo['id_riesgo']}\n")
                        f.write(f"{'-'*80}\n")
                        f.write(f"Activo Afectado: {riesgo['activo_nombre']} ({riesgo['activo_id']})\n")
                        f.write(f"Amenaza: {riesgo['amenaza_nombre']} ({riesgo['amenaza_id']})\n")
                        f.write(f"Nivel de Riesgo: {riesgo['nivel_riesgo']} ({riesgo['clasificacion']})\n")
                        f.write(f"Probabilidad: {riesgo['probabilidad']}/5\n")
                        f.write(f"Impacto: {riesgo['impacto']}/5\n")
                        f.write(f"Valor CIA del Activo: {riesgo['valor_cia']}/9\n\n")
                        
                        f.write("REQUERIMIENTO:\n")
                        f.write(f"Se requiere implementar controles para mitigar el riesgo de\n")
                        f.write(f"'{riesgo['amenaza_nombre']}' sobre el activo\n")
                        f.write(f"'{riesgo['activo_nombre']}'.\n\n")
                        
                        f.write("ACCIONES RECOMENDADAS:\n")
                        f.write("- Evaluar controles existentes\n")
                        f.write("- Identificar controles ISO 27001 Anexo A aplicables\n")
                        f.write("- Definir plan de implementación\n")
                        f.write("- Establecer indicadores de efectividad\n")
                        f.write("- Definir responsables y cronograma\n\n")
                        
                        f.write(f"{'='*80}\n\n")
        
        print(f"✓ Documento de requerimientos generado: {archivo_salida}")
        
        # También generar versión CSV
        archivo_csv = archivo_salida.replace('.txt', '.csv')
        df_requieren_control.to_csv(archivo_csv, index=False, encoding='utf-8')
        print(f"✓ Requerimientos en CSV: {archivo_csv}")
        
        return True
    
    def generar_graficos(self, df, directorio_salida):
        """Generar visualizaciones de análisis de riesgos"""
        if df is None or df.empty:
            print("✗ No hay datos para graficar")
            return
        
        print("\n" + "="*70)
        print("GENERANDO GRÁFICOS DE ANÁLISIS DE RIESGOS")
        print("="*70)
        
        # Gráfico 1: Matriz de Riesgos (Probabilidad vs Impacto)
        plt.figure(figsize=(12, 8))
        
        # Preparar datos para heatmap
        matriz = np.zeros((5, 5))
        for _, riesgo in df.iterrows():
            prob = int(riesgo['probabilidad']) - 1
            imp = int(riesgo['impacto']) - 1
            matriz[imp][prob] += 1
        
        # Crear heatmap
        ax = sns.heatmap(matriz, annot=True, fmt='.0f', cmap='RdYlGn_r',
                        cbar_kws={'label': 'Cantidad de Riesgos'},
                        linewidths=1, linecolor='black')
        
        ax.set_xlabel('Probabilidad', fontsize=12, fontweight='bold')
        ax.set_ylabel('Impacto', fontsize=12, fontweight='bold')
        ax.set_title('Matriz de Riesgos: Probabilidad vs Impacto',
                    fontsize=14, fontweight='bold')
        
        ax.set_xticklabels(['1-Muy Bajo', '2-Bajo', '3-Medio', '4-Alto', '5-Muy Alto'])
        ax.set_yticklabels(['1-Muy Bajo', '2-Bajo', '3-Medio', '4-Alto', '5-Muy Alto'])
        
        plt.tight_layout()
        archivo1 = os.path.join(directorio_salida, 'matriz_probabilidad_impacto.png')
        plt.savefig(archivo1, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo1}")
        plt.close()
        
        # Gráfico 2: Distribución de riesgos por clasificación
        plt.figure(figsize=(10, 6))
        clasificacion_orden = ['Bajo', 'Medio', 'Alto', 'Crítico']
        clasificacion_counts = df['clasificacion'].value_counts()
        
        colores = {'Bajo': 'green', 'Medio': 'yellow', 'Alto': 'orange', 'Crítico': 'red'}
        colors = [colores.get(c, 'gray') for c in clasificacion_orden]
        values = [clasificacion_counts.get(c, 0) for c in clasificacion_orden]
        
        plt.bar(clasificacion_orden, values, color=colors, edgecolor='black', linewidth=1.5)
        plt.xlabel('Clasificación de Riesgo', fontsize=12, fontweight='bold')
        plt.ylabel('Cantidad de Riesgos', fontsize=12, fontweight='bold')
        plt.title('Distribución de Riesgos por Clasificación',
                 fontsize=14, fontweight='bold')
        
        for i, v in enumerate(values):
            plt.text(i, v + 0.5, str(v), ha='center', fontweight='bold', fontsize=12)
        
        plt.tight_layout()
        archivo2 = os.path.join(directorio_salida, 'distribucion_clasificacion_riesgos.png')
        plt.savefig(archivo2, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo2}")
        plt.close()
        
        # Gráfico 3: Top 20 Riesgos Más Críticos
        plt.figure(figsize=(14, 10))
        top20 = df.nlargest(20, 'nivel_riesgo')
        
        # Crear etiquetas combinadas
        top20['etiqueta'] = top20['activo_nombre'] + ' ← ' + top20['amenaza_nombre']
        
        colors_map = {'Bajo': 'green', 'Medio': 'yellow', 'Alto': 'orange', 'Crítico': 'red'}
        colors = top20['clasificacion'].map(colors_map)
        
        plt.barh(range(len(top20)), top20['nivel_riesgo'], color=colors, edgecolor='black')
        plt.yticks(range(len(top20)), top20['etiqueta'], fontsize=8)
        plt.xlabel('Nivel de Riesgo', fontsize=12, fontweight='bold')
        plt.title('Top 20 Riesgos Más Críticos', fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        
        # Líneas de umbral
        plt.axvline(x=self.umbrales['bajo'], color='green', linestyle='--',
                   alpha=0.5, label='Umbral Bajo')
        plt.axvline(x=self.umbrales['medio'], color='yellow', linestyle='--',
                   alpha=0.5, label='Umbral Medio')
        plt.axvline(x=self.umbrales['alto'], color='orange', linestyle='--',
                   alpha=0.5, label='Umbral Alto')
        plt.axvline(x=self.umbrales['critico'], color='red', linestyle='--',
                   alpha=0.5, label='Umbral Crítico')
        plt.legend()
        
        plt.tight_layout()
        archivo3 = os.path.join(directorio_salida, 'top20_riesgos_criticos.png')
        plt.savefig(archivo3, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo3}")
        plt.close()
        
        # Gráfico 4: Riesgos por Activo
        plt.figure(figsize=(12, 8))
        riesgos_por_activo = df.groupby('activo_nombre')['nivel_riesgo'].sum().sort_values(ascending=False).head(10)
        
        plt.barh(riesgos_por_activo.index, riesgos_por_activo.values,
                color='coral', edgecolor='black')
        plt.xlabel('Nivel de Riesgo Acumulado', fontsize=12, fontweight='bold')
        plt.title('Top 10 Activos con Mayor Riesgo Acumulado',
                 fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        
        plt.tight_layout()
        archivo4 = os.path.join(directorio_salida, 'riesgos_por_activo.png')
        plt.savefig(archivo4, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo4}")
        plt.close()


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("DÍA 3: ANÁLISIS DE RIESGOS Y GENERACIÓN DE REQUERIMIENTOS")
    print("Basado en ISO/IEC 27005:2022 e ISO 31000:2018")
    print("="*70)
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Directorios
    dir_base = os.path.expanduser("~/maestria_gestion_riesgos")
    dir_resultados = os.path.join(dir_base, "resultados/dia3")
    dir_graficos = os.path.join(dir_base, "reportes/graficos")
    
    os.makedirs(dir_resultados, exist_ok=True)
    os.makedirs(dir_graficos, exist_ok=True)
    
    # Archivos de entrada
    archivo_activos = os.path.join(dir_base, "data/inventario/activos.json")
    archivo_amenazas = os.path.join(dir_base, "data/amenazas/catalogo_amenazas.json")
    
    # Crear analizador
    analizador = AnalizadorRiesgos(archivo_activos, archivo_amenazas)
    
    # Realizar análisis de riesgos
    df_riesgos = analizador.analizar_riesgos()
    
    if df_riesgos is not None and not df_riesgos.empty:
        # Generar matriz de riesgos
        archivo_matriz = os.path.join(dir_resultados, "matriz_analisis_riesgos.csv")
        analizador.generar_matriz_riesgos(df_riesgos, archivo_matriz)
        
        # Generar documento de requerimientos
        archivo_req = os.path.join(dir_resultados, "requerimientos_seguridad.txt")
        analizador.generar_requerimientos(df_riesgos, archivo_req)
        
        # Generar gráficos
        analizador.generar_graficos(df_riesgos, dir_graficos)
    
    # RESUMEN FINAL
    print("\n" + "="*70)
    print("RESUMEN DEL DÍA 3")
    print("="*70)
    print(f"✓ Riesgos analizados: {len(analizador.riesgos)}")
    print(f"✓ Matriz de riesgos generada")
    print(f"✓ Documento de requerimientos creado")
    print(f"✓ Gráficos de análisis generados")
    print(f"✓ Archivos en: {dir_resultados}")
    print(f"✓ Gráficos en: {dir_graficos}")
    print("\n📝 Próximo paso: Selección de Controles ISO 27001 (Día 4)")
    print("   Implementar controles para mitigar riesgos identificados")
    print("="*70)

if __name__ == "__main__":
    main()
