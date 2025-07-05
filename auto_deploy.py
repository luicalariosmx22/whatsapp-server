#!/usr/bin/env python3
"""
Script para elegir automáticamente la mejor configuración de deployment
"""

import os
import sys
import json

def detect_best_deployment():
    """Detectar la mejor opción de deployment"""
    
    print("🔍 Detectando mejor opción de deployment...")
    
    # Prioridad de opciones
    options = [
        {
            "name": "nixpacks básico",
            "description": "Usa nixpacks.toml con Chrome y ChromeDriver fijos",
            "files": ["nixpacks.toml"],
            "setup": lambda: setup_nixpacks_basic()
        },
        {
            "name": "Dockerfile simplificado", 
            "description": "Usa Dockerfile con versiones específicas",
            "files": ["Dockerfile"],
            "setup": lambda: setup_dockerfile_simple()
        },
        {
            "name": "Dockerfile con Selenium",
            "description": "Usa imagen de Selenium con Chrome preinstalado",
            "files": ["Dockerfile.selenium"],
            "setup": lambda: setup_dockerfile_selenium()
        },
        {
            "name": "Configuración mínima",
            "description": "Solo nixpacks mínimo sin Chrome",
            "files": ["nixpacks_simple.toml"],
            "setup": lambda: setup_minimal()
        }
    ]
    
    print("\n📋 Opciones disponibles:")
    for i, option in enumerate(options):
        print(f"{i+1}. {option['name']}: {option['description']}")
    
    # Selección automática (primera opción)
    choice = 0
    print(f"\n🎯 Seleccionando automáticamente: {options[choice]['name']}")
    
    return options[choice]

def setup_nixpacks_basic():
    """Configurar nixpacks básico"""
    print("📦 Configurando nixpacks básico...")
    
    # El archivo nixpacks.toml ya está configurado
    # Remover Dockerfile para evitar conflictos
    dockerfiles = ['Dockerfile', 'Dockerfile.simple', 'Dockerfile.selenium']
    for dockerfile in dockerfiles:
        if os.path.exists(dockerfile):
            os.rename(dockerfile, f"{dockerfile}.backup")
            print(f"   📦 {dockerfile} -> {dockerfile}.backup")
    
    print("✅ nixpacks básico configurado")

def setup_dockerfile_simple():
    """Configurar Dockerfile simplificado"""
    print("🐳 Configurando Dockerfile simplificado...")
    
    # Remover nixpacks.toml para que use Dockerfile
    if os.path.exists('nixpacks.toml'):
        os.rename('nixpacks.toml', 'nixpacks.toml.backup')
        print("   📦 nixpacks.toml -> nixpacks.toml.backup")
    
    print("✅ Dockerfile simplificado configurado")

def setup_dockerfile_selenium():
    """Configurar Dockerfile con Selenium"""
    print("🔧 Configurando Dockerfile con Selenium...")
    
    # Remover nixpacks.toml
    if os.path.exists('nixpacks.toml'):
        os.rename('nixpacks.toml', 'nixpacks.toml.backup')
    
    # Usar Dockerfile.selenium
    if os.path.exists('Dockerfile.selenium'):
        if os.path.exists('Dockerfile'):
            os.rename('Dockerfile', 'Dockerfile.backup')
        os.rename('Dockerfile.selenium', 'Dockerfile')
        print("   🐳 Dockerfile.selenium -> Dockerfile")
    
    print("✅ Dockerfile con Selenium configurado")

def setup_minimal():
    """Configurar versión mínima"""
    print("⚡ Configurando versión mínima...")
    
    # Usar nixpacks_simple.toml
    if os.path.exists('nixpacks_simple.toml'):
        if os.path.exists('nixpacks.toml'):
            os.rename('nixpacks.toml', 'nixpacks.toml.backup')
        os.rename('nixpacks_simple.toml', 'nixpacks.toml')
        print("   📦 nixpacks_simple.toml -> nixpacks.toml")
    
    # Remover Dockerfiles
    dockerfiles = ['Dockerfile', 'Dockerfile.simple', 'Dockerfile.selenium']
    for dockerfile in dockerfiles:
        if os.path.exists(dockerfile):
            os.rename(dockerfile, f"{dockerfile}.backup")
    
    print("✅ Versión mínima configurada")

def main():
    """Función principal"""
    print("🚀 Configurador automático de deployment")
    print("=" * 50)
    
    # Detectar mejor opción
    best_option = detect_best_deployment()
    
    print(f"\n🔧 Aplicando configuración: {best_option['name']}")
    print("=" * 50)
    
    # Aplicar configuración
    best_option['setup']()
    
    print("\n✅ Configuración aplicada exitosamente")
    print("💡 Próximos pasos:")
    print("   git add .")
    print("   git commit -m '🔧 Auto-configure deployment'")
    print("   git push origin main")
    print("\n🚀 Luego verifica el deployment en Railway!")

if __name__ == "__main__":
    main()
