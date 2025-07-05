#!/usr/bin/env python3
"""
Monitor en tiempo real del servidor Railway
"""

import requests
import time
import json

def monitor_railway():
    """Monitorear el servidor cada 30 segundos"""
    
    base_url = "https://whatsapp-server-production-8f61.up.railway.app"
    
    print("📡 Monitoreando servidor Railway...")
    print("🔗 URL:", base_url)
    print("⏰ Verificando cada 30 segundos...")
    print("=" * 60)
    
    routes_to_check = ["/health", "/stats", "/docs"]
    
    while True:
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n🕐 {timestamp}")
            
            all_working = True
            
            for route in routes_to_check:
                try:
                    response = requests.get(f"{base_url}{route}", timeout=5)
                    
                    if response.status_code == 200:
                        print(f"   ✅ {route} - OK")
                        
                        if route == "/health":
                            try:
                                data = response.json()
                                status = data.get('status', 'unknown')
                                sessions = data.get('active_sessions', 0)
                                print(f"      🩺 Status: {status}, Sessions: {sessions}")
                            except:
                                pass
                                
                    else:
                        print(f"   ❌ {route} - {response.status_code}")
                        all_working = False
                        
                except Exception as e:
                    print(f"   ❌ {route} - Error: {e}")
                    all_working = False
            
            if all_working:
                print("   🎉 ¡Todas las rutas funcionando!")
            else:
                print("   ⚠️  Algunas rutas tienen problemas")
            
            print("   ⏳ Esperando 30 segundos...")
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n👋 Monitoreo detenido")
            break
        except Exception as e:
            print(f"\n❌ Error en monitoreo: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_railway()
