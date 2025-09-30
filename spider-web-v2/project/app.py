from flask import Flask, render_template, jsonify, request, session
import uuid
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'clave_super_secreta'

# Almacenamiento simple en memoria
visitors = {}

def get_client_info(request):
    """Obtener información básica del cliente"""
    user_agent = request.headers.get('User-Agent', '')
    
    # Detectar navegador simple
    if 'Chrome' in user_agent:
        browser = 'Chrome'
    elif 'Firefox' in user_agent:
        browser = 'Firefox'
    elif 'Safari' in user_agent:
        browser = 'Safari'
    else:
        browser = 'Otro'
    
    # Detectar OS simple
    if 'Windows' in user_agent:
        os = 'Windows'
    elif 'Linux' in user_agent:
        os = 'Linux'
    elif 'Android' in user_agent:
        os = 'Android'
    elif 'Mac' in user_agent or 'iPhone' in user_agent:
        os = 'Mac/iOS'
    else:
        os = 'Otro'
    
    # Detectar dispositivo
    if 'Mobile' in user_agent:
        device = 'Móvil'
    elif 'Tablet' in user_agent:
        device = 'Tablet'
    else:
        device = 'Escritorio'
    
    return {
        'browser': browser,
        'os': os,
        'device': device,
        'ip': request.remote_addr,
        'language': request.headers.get('Accept-Language', ''),
        'user_agent': user_agent
    }

@app.before_request
def track_visitor():
    """SIMPLE: Crear o actualizar visitante"""
    if 'visitor_id' not in session:
        # Crear nuevo visitante
        visitor_id = str(uuid.uuid4())
        session['visitor_id'] = visitor_id
        
        client_info = get_client_info(request)
        
        visitors[visitor_id] = {
            'id': visitor_id,
            'name': f'Visitor_{visitor_id[:8]}',
            'type': 'visitor',
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'page_visits': 1,
            'engagement_score': 10.0,
            'client_info': client_info,
            'screen_resolution': request.args.get('screen', 'Unknown')
        }
        
        print(f"🆕 NUEVO VISITANTE: {visitor_id[:12]} - IP: {client_info['ip']} - {client_info['os']} - {client_info['browser']}")
    
    else:
        # Actualizar visitante existente
        visitor_id = session['visitor_id']
        if visitor_id in visitors:
            visitors[visitor_id]['page_visits'] += 1
            visitors[visitor_id]['last_seen'] = datetime.now().isoformat()
            visitors[visitor_id]['engagement_score'] = min(visitors[visitor_id]['engagement_score'] + 2, 100)
            print(f"📊 Visitante actualizado: {visitor_id[:12]} - Páginas: {visitors[visitor_id]['page_visits']}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/network')
def get_network():
    """API SIMPLE: Devuelve centro + visitantes"""
    website_center = {'id': 'website', 'name': 'Sitio Central', 'type': 'center'}
    
    nodes = [website_center]
    links = []
    
    # Solo visitantes activos (últimos 30 minutos)
    now = datetime.now()
    active_visitors = {}
    
    for visitor_id, visitor in visitors.items():
        last_seen = datetime.fromisoformat(visitor['last_seen'])
        if (now - last_seen).total_seconds() < 1800:  # 30 minutos
            active_visitors[visitor_id] = visitor
    
    # Actualizar visitors con solo activos
    visitors.clear()
    visitors.update(active_visitors)
    
    for visitor_id, visitor in visitors.items():
        nodes.append(visitor)
        links.append({
            'source': website_center['id'],
            'target': visitor_id,
            'strength': visitor['engagement_score'] / 100
        })
    
    print(f"🌐 Red activa: {len(nodes)-1} visitantes")
    return jsonify({
        'nodes': nodes,
        'links': links
    })

if __name__ == '__main__':
    print("🚀 Servidor INICIADO - Solo visitantes REALES")
    print("📊 Esperando visitantes...")
    app.run(debug=True, host='0.0.0.0', port=5000)