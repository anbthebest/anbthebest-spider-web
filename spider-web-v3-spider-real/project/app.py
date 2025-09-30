from flask import Flask, render_template, jsonify, request, session
import uuid
from datetime import datetime
import math
import random
from modules.spider_detector import create_spider_profile

app = Flask(__name__)
app.secret_key = 'spider_web_secret'

# Almacenamiento en memoria
visitors = {}

@app.before_request
def track_visitor():
    """Crear visitante para rutas principales"""
    if request.endpoint and 'static' not in request.endpoint:
        if 'visitor_id' not in session:
            visitor_id = str(uuid.uuid4())
            session['visitor_id'] = visitor_id
            
            # Obtener información detallada de la araña
            spider_profile = create_spider_profile(request)
            
            visitors[visitor_id] = {
                'id': visitor_id,
                'name': f'Spider_{visitor_id[:6]}',
                'type': 'visitor',
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'page_visits': 1,
                'engagement': 10,
                'radial_position': random.uniform(0, 2 * math.pi),
                'distance': random.randint(100, 300),
                'spider_profile': spider_profile  # <- Información detallada añadida
            }
            
            print(f"🕷️ Nueva araña detectada: {visitor_id[:8]}")
            print(f"   🌐 Navegador: {spider_profile['summary']['browser_full']}")
            print(f"   💻 SO: {spider_profile['summary']['os_full']}")
            print(f"   📱 Dispositivo: {spider_profile['summary']['device_full']}")
            print(f"   📍 IP: {spider_profile['network']['ip_address']}")
            print(f"   🛡️ Threat: {spider_profile['summary']['threat_level']}")
            
        else:
            visitor_id = session['visitor_id']
            if visitor_id in visitors:
                visitors[visitor_id]['page_visits'] += 1
                visitors[visitor_id]['last_seen'] = datetime.now().isoformat()
                visitors[visitor_id]['engagement'] = min(visitors[visitor_id]['engagement'] + 2, 100)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/spiderweb')
def get_spiderweb():
    """API que devuelve la telaraña con estructura real"""
    
    # Araña central (el sitio web)
    center_spider = {
        'id': 'queen_spider',
        'name': '🕷️ Reina Araña',
        'type': 'center',
        'size': 40,
        'color': '#8B4513'
    }
    
    nodes = [center_spider]
    links = []
    
    # Crear estructura de telaraña
    web_structure = create_web_structure()
    
    # Añadir arañas visitantes
    for visitor_id, visitor in visitors.items():
        nodes.append(visitor)
        
        # Conexión a la araña central
        links.append({
            'source': 'queen_spider',
            'target': visitor_id,
            'type': 'radial',
            'strength': visitor['engagement'] / 100
        })
        
        # Conexiones entre arañas (telaraña)
        for connection in web_structure.get(visitor_id, []):
            links.append({
                'source': visitor_id,
                'target': connection,
                'type': 'spiral',
                'strength': 0.3
            })
    
    return jsonify({
        'nodes': nodes,
        'links': links,
        'web_structure': web_structure,
        'timestamp': datetime.now().isoformat()
    })

def create_web_structure():
    """Crear estructura de telaraña entre visitantes"""
    structure = {}
    visitor_ids = list(visitors.keys())
    
    if len(visitor_ids) > 1:
        for i, visitor_id in enumerate(visitor_ids):
            connections = []
            
            # Conectar con vecinos cercanos
            if i > 0:
                connections.append(visitor_ids[i-1])
            if i < len(visitor_ids) - 1:
                connections.append(visitor_ids[i+1])
                
            # Conexiones aleatorias adicionales
            if len(visitor_ids) > 2:
                possible_connections = [v for v in visitor_ids if v != visitor_id]
                extra_connections = random.sample(possible_connections, 
                                                min(2, len(possible_connections)))
                connections.extend(extra_connections)
            
            structure[visitor_id] = list(set(connections))
    
    return structure

@app.route('/api/add_spider')
def add_spider():
    """Añadir una araña de prueba con datos reales"""
    visitor_id = str(uuid.uuid4())
    
    # Crear perfil de araña de prueba
    spider_profile = {
        'browser': {'name': 'Google Chrome', 'version': '119.0.0.0', 'engine': 'Blink'},
        'operating_system': {'name': 'Windows 10/11', 'version': '10', 'architecture': '64-bit'},
        'device': {'type': 'Desktop', 'model': 'Unknown', 'brand': 'Unknown', 'is_mobile': False, 'is_tablet': False},
        'network': {'ip_address': '192.168.1.100', 'type': 'VPN/Local', 'is_proxy': False, 'is_vpn': True, 'country': 'Local Network', 'threat_level': 'Low'},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'summary': {
            'browser_full': 'Google Chrome 119.0.0.0',
            'os_full': 'Windows 10/11 10',
            'device_full': 'Unknown Unknown (Desktop)',
            'network_type': 'VPN/Local',
            'threat_level': 'Low'
        }
    }
    
    visitors[visitor_id] = {
        'id': visitor_id,
        'name': f'Spider_{visitor_id[:6]}',
        'type': 'visitor',
        'first_seen': datetime.now().isoformat(),
        'last_seen': datetime.now().isoformat(),
        'page_visits': 1,
        'engagement': random.randint(10, 50),
        'radial_position': random.uniform(0, 2 * math.pi),
        'distance': random.randint(100, 300),
        'spider_profile': spider_profile
    }
    
    print(f"🕷️ Araña de prueba añadida: {visitor_id[:8]}")
    return jsonify({'status': 'spider_added', 'spider_id': visitor_id})

if __name__ == '__main__':
    print("🕸️  Spider Web con Detector iniciada: http://localhost:5000")
    print("🕷️  Detectando arañas en tiempo real...")
    app.run(debug=True, port=5000)