#!/usr/bin/env python3
"""
DÍA 2: Identificación y Valoración de Activos
Basado en ISO/IEC 27005 y la triada CIA
"""

import json
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuración de estilo
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

class GestorActivos:
    """Clase para gestionar inventario y valoración de activos"""
    
    def __init__(self, archivo_activos):
        self.archivo_activos = archivo_activos
        self.activos = self.cargar_activos()
        
        # Valores numéricos para CIA
        self.valores_cia = {
            'bajo': 1,
            'medio': 2,
            'alto': 3
        }
    
    def cargar_activos(self):
        """Cargar activos desde archivo JSON"""
        try:
            with open(self.archivo_activos, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['activos']
        except FileNotFoundError:
            print(f"✗ Error: No se encontró {self.archivo_activos}")
            return []
        except json.JSONDecodeError:
            print(f"✗ Error: Archivo JSON mal formado")
            return []
    
    def calcular_valor_cia(self, activo):
        """Calcular valor CIA de un activo"""
        c = self.valores_cia.get(activo['confidencialidad'], 0)
        i = self.valores_cia.get(activo['integridad'], 0)
        a = self.valores_cia.get(activo['disponibilidad'], 0)
        
        # Valor CIA = suma de los tres componentes
        valor_cia = c + i + a
        
        # Valor CIA ponderado (0-100)
        valor_cia_ponderado = (valor_cia / 9) * 100
        
        return {
            'valor_c': c,
            'valor_i': i,
            'valor_a': a,
            'valor_cia_total': valor_cia,
            'valor_cia_ponderado': round(valor_cia_ponderado, 2)
        }
    
    def analizar_inventario(self):
        """Analizar inventario de activos"""
        if not self.activos:
            print("✗ No hay activos para analizar")
            return None
        
        print("\n" + "="*70)
        print("ANÁLISIS DEL INVENTARIO DE ACTIVOS")
        print("="*70)
        
        # Calcular valores CIA para todos los activos
        for activo in self.activos:
            valores = self.calcular_valor_cia(activo)
            activo.update(valores)
        
        df = pd.DataFrame(self.activos)
        
        print(f"\nTotal de activos inventariados: {len(self.activos)}")
        
        print(f"\n📊 Distribución por tipo:")
        print(df['tipo'].value_counts())
        
        print(f"\n📊 Distribución por categoría:")
        print(df['categoria'].value_counts())
        
        print(f"\n📊 Distribución por criticidad:")
        print(df['criticidad'].value_counts())
        
        print(f"\n💰 Valor monetario total: ${df['valor_monetario'].sum():,.2f}")
        print(f"   Valor promedio por activo: ${df['valor_monetario'].mean():,.2f}")
        
        print(f"\n🔐 Valor CIA promedio: {df['valor_cia_ponderado'].mean():.2f}%")
        
        # Activos más críticos
        print(f"\n🚨 Top 5 Activos Más Críticos (por valor CIA):")
        top_criticos = df.nlargest(5, 'valor_cia_ponderado')[['id', 'nombre', 'valor_cia_ponderado']]
        for idx, row in top_criticos.iterrows():
            print(f"   {row['id']} - {row['nombre']}: {row['valor_cia_ponderado']}%")
        
        return df
    
    def generar_matriz_valoracion(self, df, archivo_salida):
        """Generar matriz de valoración de activos"""
        if df is None or df.empty:
            print("✗ No hay datos para generar matriz")
            return False
        
        print("\n" + "="*70)
        print("MATRIZ DE VALORACIÓN DE ACTIVOS")
        print("="*70)
        
        # Crear matriz con información clave
        matriz = df[['id', 'nombre', 'tipo', 'criticidad', 
                     'confidencialidad', 'integridad', 'disponibilidad',
                     'valor_cia_total', 'valor_cia_ponderado', 'valor_monetario']].copy()
        
        # Ordenar por valor CIA
        matriz = matriz.sort_values('valor_cia_ponderado', ascending=False)
        
        print(f"\n{matriz.to_string(index=False)}")
        
        # Exportar a CSV
        matriz.to_csv(archivo_salida, index=False, encoding='utf-8')
        print(f"\n✓ Matriz exportada a: {archivo_salida}")
        
        return True
    
    def exportar_a_excel(self, df, archivo_salida):
        """Exportar inventario completo a Excel"""
        if df is None or df.empty:
            print("✗ No hay datos para exportar")
            return False
        
        try:
            with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
                # Hoja 1: Inventario completo
                df.to_excel(writer, sheet_name='Inventario', index=False)
                
                # Hoja 2: Resumen por tipo
                resumen_tipo = df.groupby('tipo').agg({
                    'id': 'count',
                    'valor_monetario': 'sum',
                    'valor_cia_ponderado': 'mean'
                }).rename(columns={
                    'id': 'Cantidad',
                    'valor_monetario': 'Valor Total',
                    'valor_cia_ponderado': 'CIA Promedio'
                })
                resumen_tipo.to_excel(writer, sheet_name='Resumen por Tipo')
                
                # Hoja 3: Resumen por criticidad
                resumen_crit = df.groupby('criticidad').agg({
                    'id': 'count',
                    'valor_monetario': 'sum',
                    'valor_cia_ponderado': 'mean'
                }).rename(columns={
                    'id': 'Cantidad',
                    'valor_monetario': 'Valor Total',
                    'valor_cia_ponderado': 'CIA Promedio'
                })
                resumen_crit.to_excel(writer, sheet_name='Resumen por Criticidad')
            
            print(f"✓ Inventario exportado a Excel: {archivo_salida}")
            return True
            
        except Exception as e:
            print(f"✗ Error al exportar a Excel: {e}")
            return False
    
    def generar_graficos(self, df, directorio_salida):
        """Generar gráficos de valoración"""
        if df is None or df.empty:
            print("✗ No hay datos para graficar")
            return
        
        print("\n" + "="*70)
        print("GENERANDO GRÁFICOS DE VALORACIÓN")
        print("="*70)
        
        # Gráfico 1: Valor CIA por activo
        plt.figure(figsize=(14, 8))
        df_sorted = df.sort_values('valor_cia_ponderado', ascending=True)
        colors = plt.cm.RdYlGn_r(df_sorted['valor_cia_ponderado'] / 100)
        
        plt.barh(df_sorted['nombre'], df_sorted['valor_cia_ponderado'], color=colors)
        plt.xlabel('Valor CIA Ponderado (%)')
        plt.title('Valoración CIA de Activos', fontsize=14, fontweight='bold')
        plt.xlim(0, 100)
        
        # Agregar líneas de referencia
        plt.axvline(x=33, color='green', linestyle='--', alpha=0.3, label='Bajo')
        plt.axvline(x=66, color='orange', linestyle='--', alpha=0.3, label='Medio')
        plt.axvline(x=90, color='red', linestyle='--', alpha=0.3, label='Alto')
        plt.legend()
        
        plt.tight_layout()
        archivo1 = os.path.join(directorio_salida, 'valoracion_cia_activos.png')
        plt.savefig(archivo1, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo1}")
        plt.close()
        
        # Gráfico 2: Distribución CIA (Radar Chart)
        plt.figure(figsize=(12, 8))
        
        # Calcular promedios por componente CIA
        avg_c = df['valor_c'].mean()
        avg_i = df['valor_i'].mean()
        avg_a = df['valor_a'].mean()
        
        categories = ['Confidencialidad', 'Integridad', 'Disponibilidad']
        values = [avg_c, avg_i, avg_a]
        values += values[:1]  # Cerrar el polígono
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        ax = plt.subplot(111, projection='polar')
        ax.plot(angles, values, 'o-', linewidth=2, color='blue')
        ax.fill(angles, values, alpha=0.25, color='blue')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 3)
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(['Bajo', 'Medio', 'Alto'])
        ax.grid(True)
        plt.title('Perfil Promedio CIA de la Organización', 
                 size=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        archivo2 = os.path.join(directorio_salida, 'perfil_cia_organizacion.png')
        plt.savefig(archivo2, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo2}")
        plt.close()
        
        # Gráfico 3: Valor monetario vs Valor CIA
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(df['valor_monetario'], df['valor_cia_ponderado'],
                            s=200, c=df['valor_cia_ponderado'], 
                            cmap='RdYlGn_r', alpha=0.6, edgecolors='black')
        
        # Etiquetar puntos
        for idx, row in df.iterrows():
            plt.annotate(row['id'], 
                        (row['valor_monetario'], row['valor_cia_ponderado']),
                        fontsize=8, ha='center')
        
        plt.xlabel('Valor Monetario ($)', fontsize=12)
        plt.ylabel('Valor CIA Ponderado (%)', fontsize=12)
        plt.title('Correlación: Valor Monetario vs Valor CIA', 
                 fontsize=14, fontweight='bold')
        plt.colorbar(scatter, label='Valor CIA (%)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        archivo3 = os.path.join(directorio_salida, 'correlacion_valor_cia.png')
        plt.savefig(archivo3, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo3}")
        plt.close()
        
        # Gráfico 4: Distribución por criticidad
        plt.figure(figsize=(10, 6))
        criticidad_orden = ['bajo', 'medio', 'alto', 'critico']
        criticidad_counts = df['criticidad'].value_counts()
        
        # Asegurar el orden correcto
        criticidad_ordenada = [criticidad_counts.get(c, 0) for c in criticidad_orden]
        colors_crit = ['green', 'yellow', 'orange', 'red']
        
        plt.bar(criticidad_orden, criticidad_ordenada, color=colors_crit, edgecolor='black')
        plt.xlabel('Nivel de Criticidad', fontsize=12)
        plt.ylabel('Cantidad de Activos', fontsize=12)
        plt.title('Distribución de Activos por Criticidad', 
                 fontsize=14, fontweight='bold')
        
        # Agregar valores sobre las barras
        for i, v in enumerate(criticidad_ordenada):
            plt.text(i, v + 0.1, str(v), ha='center', fontweight='bold')
        
        plt.tight_layout()
        archivo4 = os.path.join(directorio_salida, 'distribucion_criticidad.png')
        plt.savefig(archivo4, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo4}")
        plt.close()


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("DÍA 2: IDENTIFICACIÓN Y VALORACIÓN DE ACTIVOS")
    print("Basado en ISO/IEC 27005:2022 y Triada CIA")
    print("="*70)
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Directorios
    dir_base = os.path.expanduser("~/maestria_gestion_riesgos")
    dir_resultados = os.path.join(dir_base, "resultados/dia2")
    dir_reportes = os.path.join(dir_base, "reportes")
    dir_graficos = os.path.join(dir_reportes, "graficos")
    
    # Crear directorios
    os.makedirs(dir_resultados, exist_ok=True)
    os.makedirs(dir_graficos, exist_ok=True)
    
    # Archivo de activos
    archivo_activos = os.path.join(dir_base, "data/inventario/activos.json")
    
    # Crear gestor de activos
    gestor = GestorActivos(archivo_activos)
    
    # Analizar inventario
    df = gestor.analizar_inventario()
    
    if df is not None and not df.empty:
        # Generar matriz de valoración
        archivo_matriz = os.path.join(dir_resultados, "matriz_valoracion_activos.csv")
        gestor.generar_matriz_valoracion(df, archivo_matriz)
        
        # Exportar a Excel
        archivo_excel = os.path.join(dir_resultados, "inventario_activos_completo.xlsx")
        gestor.exportar_a_excel(df, archivo_excel)
        
        # Generar gráficos
        gestor.generar_graficos(df, dir_graficos)
    
    # RESUMEN FINAL
    print("\n" + "="*70)
    print("RESUMEN DEL DÍA 2")
    print("="*70)
    print(f"✓ Activos inventariados: {len(gestor.activos)}")
    print(f"✓ Matriz de valoración generada")
    print(f"✓ Inventario exportado a Excel")
    print(f"✓ Gráficos de criticidad generados")
    print(f"✓ Archivos en: {dir_resultados}")
    print(f"✓ Gráficos en: {dir_graficos}")
    print("\n📝 Próximo paso: Análisis de Riesgos (Día 3)")
    print("   Relacionar amenazas (Día 1) con activos (Día 2)")
    print("="*70)

if __name__ == "__main__":
    main()
