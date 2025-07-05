# ✅ Archivo: clientes/aura/routes/panel_cliente_qr_whatsapp_web/__init__.py
# 👉 Módulo para integrar WhatsApp Web con QR dentro del panel de Nora

from flask import Blueprint, render_template, request, session, redirect, jsonify
from clientes.aura.utils.supabase_client import supabase
import qrcode
import io
import base64
import json
from datetime import datetime

# Crear el blueprint
panel_cliente_qr_whatsapp_web_bp = Blueprint('panel_cliente_qr_whatsapp_web', __name__)

@panel_cliente_qr_whatsapp_web_bp.route('/')
def index():
    """Vista principal del módulo QR WhatsApp Web"""
    # Obtener nombre_nora desde la URL path
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Verificar que el módulo esté disponible globalmente
        modulo_disponible = supabase.table("modulos_disponibles")\
            .select("*")\
            .eq("nombre", "qr_whatsapp_web")\
            .execute()
        
        if not modulo_disponible.data:
            return redirect(f"/panel_cliente/{nombre_nora}")
        
        # Verificar si el módulo está activo para esta Nora específica
        config_bot = supabase.table("configuracion_bot")\
            .select("modulos")\
            .eq("nombre_nora", nombre_nora)\
            .execute()
        
        if config_bot.data:
            modulos_activos = config_bot.data[0].get("modulos", [])
            if isinstance(modulos_activos, str):
                modulos_activos = [m.strip() for m in modulos_activos.split(",")]
            
            if "qr_whatsapp_web" not in modulos_activos:
                return redirect(f"/panel_cliente/{nombre_nora}")
        else:
            return redirect(f"/panel_cliente/{nombre_nora}")
        
        # Obtener configuración de WhatsApp Web para esta Nora
        config_whatsapp = supabase.table("whatsapp_web_sessions")\
            .select("*")\
            .eq("nombre_nora", nombre_nora)\
            .execute()
        
        session_data = config_whatsapp.data[0] if config_whatsapp.data else None
        
        return render_template('panel_cliente_qr_whatsapp_web/index_websocket.html',
                             nombre_nora=nombre_nora,
                             session_data=session_data)
        
    except Exception as e:
        print(f"❌ Error en módulo QR WhatsApp Web para {nombre_nora}: {str(e)}")
        return redirect(f"/panel_cliente/{nombre_nora}")

@panel_cliente_qr_whatsapp_web_bp.route('/generar_qr', methods=['POST'])
def generar_qr():
    """Genera un nuevo QR para WhatsApp Web"""
    # Obtener nombre_nora desde la URL path
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Generar un código único para esta sesión
        import uuid
        session_id = str(uuid.uuid4())
        
        # Para WhatsApp Web real, necesitaríamos implementar el protocolo WebSocket
        # Por ahora, generamos un QR con información de contacto o un mensaje
        # Esto abrirá WhatsApp Web o la app con un mensaje predefinido
        
        # Opción 1: QR para abrir chat directo (necesita número de teléfono)
        # whatsapp_url = f"https://wa.me/?text=Hola, me gustaría conectar mi WhatsApp con Nora ({nombre_nora})"
        
        # Opción 2: QR con información de conexión para mostrar al usuario
        conexion_info = {
            "nora": nombre_nora,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "action": "whatsapp_web_connection"
        }
        
        # Crear un QR con información JSON o URL personalizada
        qr_data = f"NORA_WA_CONNECTION:{json.dumps(conexion_info)}"
        
        # Generar QR code
        qr = qrcode.QRCode(
            version=2,  # Aumentar versión para más datos
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Crear imagen del QR
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Guardar sesión en base de datos
        session_data = {
            "nombre_nora": nombre_nora,
            "session_id": session_id,
            "qr_code": qr_base64,
            "qr_data": qr_data,
            "estado": "pending",
            "fecha_generacion": datetime.now().isoformat(),
            "connection_info": json.dumps(conexion_info)
        }
        
        # Insertar o actualizar sesión
        existing = supabase.table("whatsapp_web_sessions")\
            .select("id")\
            .eq("nombre_nora", nombre_nora)\
            .execute()
        
        if existing.data:
            supabase.table("whatsapp_web_sessions")\
                .update(session_data)\
                .eq("nombre_nora", nombre_nora)\
                .execute()
        else:
            supabase.table("whatsapp_web_sessions")\
                .insert(session_data)\
                .execute()
        
        return jsonify({
            "success": True,
            "qr_code": qr_base64,
            "session_id": session_id,
            "message": "QR generado correctamente"
        })
        
    except Exception as e:
        print(f"❌ Error generando QR: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_qr_whatsapp_web_bp.route('/verificar_estado', methods=['GET'])
def verificar_estado():
    """Verifica el estado de la sesión de WhatsApp Web"""
    # Obtener nombre_nora desde la URL path
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Obtener estado actual de la sesión
        session_data = supabase.table("whatsapp_web_sessions")\
            .select("*")\
            .eq("nombre_nora", nombre_nora)\
            .execute()
        
        if not session_data.data:
            return jsonify({
                "success": False,
                "estado": "no_session",
                "message": "No hay sesión activa"
            })
        
        session = session_data.data[0]
        
        # Simular verificación de estado (en implementación real conectarías con WhatsApp)
        estado = session.get("estado", "pending")
        
        return jsonify({
            "success": True,
            "estado": estado,
            "session_id": session.get("session_id"),
            "fecha_generacion": session.get("fecha_generacion")
        })
        
    except Exception as e:
        print(f"❌ Error verificando estado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_qr_whatsapp_web_bp.route('/desconectar', methods=['POST'])
def desconectar():
    """Desconecta la sesión de WhatsApp Web"""
    # Obtener nombre_nora desde la URL path
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Actualizar estado a desconectado
        supabase.table("whatsapp_web_sessions")\
            .update({
                "estado": "disconnected",
                "fecha_desconexion": datetime.now().isoformat()
            })\
            .eq("nombre_nora", nombre_nora)\
            .execute()
        
        return jsonify({
            "success": True,
            "message": "Sesión desconectada correctamente"
        })
        
    except Exception as e:
        print(f"❌ Error desconectando: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_qr_whatsapp_web_bp.route('/generar_qr_whatsapp', methods=['POST'])
def generar_qr_whatsapp():
    """Genera un QR para abrir WhatsApp con un mensaje predefinido"""
    # Obtener nombre_nora desde la URL path
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Obtener configuración básica de la Nora
        config_bot = supabase.table("configuracion_bot")\
            .select("empresa, telefono")\
            .eq("nombre_nora", nombre_nora)\
            .execute()
        
        empresa = nombre_nora
        telefono = None
        
        if config_bot.data:
            empresa = config_bot.data[0].get("empresa", nombre_nora)
            telefono = config_bot.data[0].get("telefono")
        
        # Mensaje predefinido para WhatsApp
        mensaje = f"¡Hola! Quiero conectar mi WhatsApp con Nora ({empresa}). ¿Puedes ayudarme?"
        
        # URL de WhatsApp con mensaje predefinido
        if telefono:
            # Si hay teléfono configurado, crear enlace directo al número
            whatsapp_url = f"https://wa.me/{telefono.replace('+', '').replace(' ', '')}?text={mensaje}"
        else:
            # Sin número específico, solo el mensaje
            whatsapp_url = f"https://wa.me/?text={mensaje}"
        
        # Generar QR code para WhatsApp
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        qr.add_data(whatsapp_url)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            "success": True,
            "qr_code": img_base64,
            "whatsapp_url": whatsapp_url,
            "message": "QR de WhatsApp generado correctamente"
        })
        
    except Exception as e:
        print(f"❌ Error generando QR WhatsApp para {nombre_nora}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
