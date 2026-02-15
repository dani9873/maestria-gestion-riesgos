#!/usr/bin/env python3
"""
DÍA 1: Identificación de Amenazas y Vulnerabilidades
Basado en ISO/IEC 27005 y buenas prácticas de seguridad
"""

import json
import csv
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de estilo para gráficos
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

class GestorAmenazas:
    """Clase para gestionar el catálogo de amenazas"""
    
    def __init__(self, archivo_amenazas):
        self.archivo_amenazas = archivo_amenazas
        self.amenazas = self.cargar_amenazas()
    
    def cargar_amenazas(self):
        """Cargar amenazas desde archivo JSON"""
        try:
            with open(self.archivo_amenazas, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['amenazas']
        except FileNotFoundError:
            print(f"✗ Error: No se encontró el archivo {self.archivo_amenazas}")
            return []
        except json.JSONDecodeError:
            print(f"✗ Error: Archivo JSON mal formado")
            return []
    
    def analizar_amenazas(self):
        """Analizar distribución de amenazas"""
        if not self.amenazas:
            print("✗ No hay amenazas para analizar")
            return None
        
        df = pd.DataFrame(self.amenazas)
        
        print("\n" + "="*70)
        print("ANÁLISIS DE AMENAZAS IDENTIFICADAS")
        print("="*70)
        
        print(f"\nTotal de amenazas catalogadas: {len(self.amenazas)}")
        print(f"\nDistribución por tipo:")
        print(df['tipo'].value_counts())
        
        print(f"\nDistribución por categoría:")
        print(df['categoria'].value_counts())
        
        print(f"\nDistribución por fuente:")
        print(df['fuente'].value_counts())
        
        print(f"\nNivel de probabilidad promedio: {df['probabilidad'].mean():.2f}")
        
        return df
    
    def exportar_csv(self, archivo_salida):
        """Exportar amenazas a CSV"""
        if not self.amenazas:
            print("✗ No hay amenazas para exportar")
            return False
        
        df = pd.DataFrame(self.amenazas)
        df.to_csv(archivo_salida, index=False, encoding='utf-8')
        print(f"✓ Amenazas exportadas a: {archivo_salida}")
        return True
    
    def generar_graficos(self, directorio_salida):
        """Generar visualizaciones de amenazas"""
        if not self.amenazas:
            print("✗ No hay amenazas para graficar")
            return
        
        df = pd.DataFrame(self.amenazas)
        
        # Gráfico 1: Amenazas por tipo
        plt.figure(figsize=(10, 6))
        tipo_counts = df['tipo'].value_counts()
        plt.bar(range(len(tipo_counts)), tipo_counts.values)
        plt.xlabel('Tipo de Amenaza')
        plt.ylabel('Cantidad')
        plt.title('Distribución de Amenazas por Tipo')
        plt.xticks(range(len(tipo_counts)), tipo_counts.index, rotation=45, ha='right')
        plt.tight_layout()
        archivo1 = os.path.join(directorio_salida, 'amenazas_por_tipo.png')
        plt.savefig(archivo1, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo1}")
        plt.close()
        
        # Gráfico 2: Probabilidad de amenazas
        plt.figure(figsize=(12, 6))
        df_sorted = df.sort_values('probabilidad', ascending=False)
        plt.barh(df_sorted['nombre'], df_sorted['probabilidad'], color='coral')
        plt.xlabel('Nivel de Probabilidad (1-5)')
        plt.title('Probabilidad de Ocurrencia por Amenaza')
        plt.tight_layout()
        archivo2 = os.path.join(directorio_salida, 'probabilidad_amenazas.png')
        plt.savefig(archivo2, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {archivo2}")
        plt.close()


class EscanerVulnerabilidades:
    """Clase para realizar escaneo básico de vulnerabilidades"""
    
    def __init__(self):
        self.resultados = []
    
    def escanear_puertos_localhost(self):
        """
        Escaneo ético de puertos en localhost
        IMPORTANTE: Solo para fines educativos en entorno controlado
        """
        print("\n" + "="*70)
        print("ESCANEO DE PUERTOS - LOCALHOST")
        print("="*70)
        print("⚠️  SOLO PARA FINES EDUCATIVOS EN ENTORNO CONTROLADO")
        print("⚠️  NO ESCANEAR SISTEMAS SIN AUTORIZACIÓN EXPLÍCITA")
        print()
        
        try:
            import nmap
            nm = nmap.PortScanner()
            
            print("🔍 Escaneando puertos comunes en 127.0.0.1...")
            
            # Escanear solo puertos comunes
            nm.scan('127.0.0.1', '22,80,443,3306,5432,8080')
            
            for host in nm.all_hosts():
                print(f'\n📍 Host: {host} ({nm[host].hostname()})')
                print(f'   Estado: {nm[host].state()}')
                
                for proto in nm[host].all_protocols():
                    print(f'\n   Protocolo: {proto}')
                    
                    lport = nm[host][proto].keys()
                    for port in sorted(lport):
                        estado = nm[host][proto][port]['state']
                        servicio = nm[host][proto][port]['name']
                        
                        self.resultados.append({
                            'host': host,
                            'puerto': port,
                            'estado': estado,
                            'servicio': servicio,
                            'protocolo': proto
                        })
                        
                        print(f'   Puerto {port}: {estado} - {servicio}')
            
            return True
            
        except ImportError:
            print("✗ Error: python-nmap no está instalado")
            print("  Instalar con: pip install python-nmap")
            return False
        except Exception as e:
            print(f"✗ Error durante el escaneo: {e}")
            return False
    
    def identificar_vulnerabilidades_comunes(self):
        """Identificar vulnerabilidades comunes basadas en puertos abiertos"""
        print("\n" + "="*70)
        print("IDENTIFICACIÓN DE VULNERABILIDADES POTENCIALES")
        print("="*70)
        
        vulnerabilidades = []
        
        for resultado in self.resultados:
            if resultado['estado'] == 'open':
                vuln = {
                    'id': f"V{resultado['puerto']:04d}",
                    'servicio': resultado['servicio'],
                    'puerto': resultado['puerto'],
                    'descripcion': f"Puerto {resultado['puerto']} abierto ({resultado['servicio']})",
                    'riesgo': 'Medio',
                    'recomendacion': f"Verificar si el servicio {resultado['servicio']} es necesario"
                }
                vulnerabilidades.append(vuln)
                
                print(f"\n🔓 Vulnerabilidad potencial detectada:")
                print(f"   ID: {vuln['id']}")
                print(f"   Servicio: {vuln['servicio']}")
                print(f"   Puerto: {vuln['puerto']}")
                print(f"   Riesgo: {vuln['riesgo']}")
                print(f"   Recomendación: {vuln['recomendacion']}")
        
        if not vulnerabilidades:
            print("\n✓ No se detectaron puertos abiertos vulnerables")
        
        return vulnerabilidades
    
    def exportar_resultados(self, archivo_salida):
        """Exportar resultados del escaneo"""
        if not self.resultados:
            print("✗ No hay resultados para exportar")
            return False
        
        df = pd.DataFrame(self.resultados)
        df.to_csv(archivo_salida, index=False, encoding='utf-8')
        print(f"\n✓ Resultados exportados a: {archivo_salida}")
        return True


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("DÍA 1: IDENTIFICACIÓN DE AMENAZAS Y VULNERABILIDADES")
    print("Basado en ISO/IEC 27005:2022")
    print("="*70)
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Directorios
    dir_base = os.path.expanduser("~/maestria_gestion_riesgos")
    dir_resultados = os.path.join(dir_base, "resultados/dia1")
    dir_reportes = os.path.join(dir_base, "reportes")
    dir_graficos = os.path.join(dir_reportes, "graficos")
    
    # Crear directorios si no existen
    os.makedirs(dir_resultados, exist_ok=True)
    os.makedirs(dir_graficos, exist_ok=True)
    
    # PARTE 1: Gestión de Amenazas
    print("\n" + "-"*70)
    print("PARTE 1: ANÁLISIS DE AMENAZAS")
    print("-"*70)
    
    archivo_amenazas = os.path.join(dir_base, "data/amenazas/catalogo_amenazas.json")
    gestor = GestorAmenazas(archivo_amenazas)
    
    # Analizar amenazas
    df_amenazas = gestor.analizar_amenazas()
    
    # Exportar a CSV
    if df_amenazas is not None:
        archivo_csv = os.path.join(dir_resultados, "amenazas_identificadas.csv")
        gestor.exportar_csv(archivo_csv)
        
        # Generar gráficos
        gestor.generar_graficos(dir_graficos)
    
    # PARTE 2: Escaneo de Vulnerabilidades
    print("\n" + "-"*70)
    print("PARTE 2: ESCANEO DE VULNERABILIDADES")
    print("-"*70)
    
    escaner = EscanerVulnerabilidades()
    
    # Realizar escaneo
    if escaner.escanear_puertos_localhost():
        # Identificar vulnerabilidades
        vulnerabilidades = escaner.identificar_vulnerabilidades_comunes()
        
        # Exportar resultados del escaneo
        archivo_escaneo = os.path.join(dir_resultados, "escaneo_puertos.csv")
        escaner.exportar_resultados(archivo_escaneo)
        
        # Exportar vulnerabilidades
        if vulnerabilidades:
            df_vuln = pd.DataFrame(vulnerabilidades)
            archivo_vuln = os.path.join(dir_resultados, "vulnerabilidades_detectadas.csv")
            df_vuln.to_csv(archivo_vuln, index=False, encoding='utf-8')
            print(f"✓ Vulnerabilidades exportadas a: {archivo_vuln}")
    
    # RESUMEN FINAL
    print("\n" + "="*70)
    print("RESUMEN DEL DÍA 1")
    print("="*70)
    print(f"✓ Amenazas catalogadas: {len(gestor.amenazas)}")
    print(f"✓ Puertos escaneados: {len(escaner.resultados)}")
    print(f"✓ Archivos generados en: {dir_resultados}")
    print(f"✓ Gráficos generados en: {dir_graficos}")
    print("\n📝 Próximo paso: Revisar resultados y preparar inventario de activos (Día 2)")
    print("="*70)

if __name__ == "__main__":
    main()
