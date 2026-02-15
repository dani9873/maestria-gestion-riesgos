#!/usr/bin/env python3
"""
Script de verificación del entorno de trabajo
Verifica que todas las librerías necesarias están instaladas
"""

import sys

def verificar_libreria(nombre_libreria):
    try:
        __import__(nombre_libreria)
        print(f"✓ {nombre_libreria:<20} - INSTALADO")
        return True
    except ImportError:
        print(f"✗ {nombre_libreria:<20} - NO INSTALADO")
        return False

def main():
    print("="*60)
    print("VERIFICACIÓN DEL ENTORNO DE TRABAJO")
    print("="*60)
    print()
    
    # Verificar versión de Python
    print(f"Versión de Python: {sys.version}")
    print()
    
    # Lista de librerías necesarias
    librerias = [
        'requests',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'reportlab',
        'openpyxl',
        'PIL',
        'nmap',
        'tabulate'
    ]
    
    print("Verificando librerías:")
    print("-" * 60)
    
    resultados = [verificar_libreria(lib) for lib in librerias]
    
    print("-" * 60)
    print()
    
    if all(resultados):
        print("✓ Todas las librerías están instaladas correctamente")
        print("✓ El entorno está listo para comenzar")
        return 0
    else:
        print("✗ Algunas librerías faltan. Instálalas con:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
