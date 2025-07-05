#!/bin/bash
# Script para preparar diferentes opciones de deploy

echo "🚀 Preparando deploy para Railway..."
echo "Selecciona una opción:"
echo "1. Usar nixpacks.toml (recomendado)"
echo "2. Usar Dockerfile original"
echo "3. Usar Dockerfile simplificado"
echo "4. Usar configuración mínima"

read -p "Opción (1-4): " option

case $option in
    1)
        echo "📦 Usando nixpacks.toml..."
        # Mantener nixpacks.toml actual
        ;;
    2)
        echo "🐳 Usando Dockerfile original..."
        rm -f nixpacks.toml
        ;;
    3)
        echo "🐳 Usando Dockerfile simplificado..."
        rm -f nixpacks.toml
        mv Dockerfile Dockerfile.original
        mv Dockerfile.simple Dockerfile
        ;;
    4)
        echo "⚡ Usando configuración mínima..."
        rm -f nixpacks.toml
        mv nixpacks_simple.toml nixpacks.toml
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo "✅ Configuración preparada"
echo "💡 Ahora ejecuta:"
echo "   git add ."
echo "   git commit -m 'Fix Chrome installation'"
echo "   git push origin main"
