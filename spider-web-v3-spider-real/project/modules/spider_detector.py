import re
from typing import Dict, Any

class SpiderDetector:
    def __init__(self):
        self.browser_patterns = {
            'chrome': (r'Chrome/([\d\.]+)', 'Google Chrome'),
            'firefox': (r'Firefox/([\d\.]+)', 'Mozilla Firefox'),
            'safari': (r'Safari/([\d\.]+)', 'Apple Safari'),
            'edge': (r'Edg/([\d\.]+)', 'Microsoft Edge'),
            'opera': (r'OPR/([\d\.]+)', 'Opera'),
            'samsung': (r'SamsungBrowser/([\d\.]+)', 'Samsung Browser')
        }
        
        self.os_patterns = {
            'windows': [
                (r'Windows NT 10.0', 'Windows 10/11'),
                (r'Windows NT 6.3', 'Windows 8.1'),
                (r'Windows NT 6.2', 'Windows 8'),
                (r'Windows NT 6.1', 'Windows 7'),
                (r'Windows NT 6.0', 'Windows Vista'),
                (r'Windows NT 5.1', 'Windows XP')
            ],
            'mac': [
                (r'Mac OS X 10_15', 'macOS Catalina'),
                (r'Mac OS X 10_14', 'macOS Mojave'),
                (r'Mac OS X 10_13', 'macOS High Sierra'),
                (r'Mac OS X', 'macOS')
            ],
            'linux': [
                (r'Linux x86_64', 'Linux 64-bit'),
                (r'Linux i686', 'Linux 32-bit'),
                (r'Ubuntu', 'Ubuntu'),
                (r'Fedora', 'Fedora')
            ],
            'android': [
                (r'Android 1[0-3]', 'Android 10-13'),
                (r'Android 9', 'Android Pie'),
                (r'Android 8', 'Android Oreo')
            ],
            'ios': [
                (r'iPhone OS 1[4-6]', 'iOS 14-16'),
                (r'iPhone OS 13', 'iOS 13'),
                (r'iPhone OS 12', 'iOS 12')
            ]
        }
        
        self.device_types = {
            'mobile': ['mobile', 'android', 'iphone', 'blackberry'],
            'tablet': ['tablet', 'ipad'],
            'desktop': ['windows', 'macintosh', 'linux', 'x11']
        }

    def detect_browser(self, user_agent: str) -> Dict[str, str]:
        """Detectar navegador y versión"""
        browser_info = {
            'name': 'Unknown Browser',
            'version': 'Unknown',
            'engine': 'Unknown'
        }
        
        # Detectar motor
        if 'webkit' in user_agent.lower():
            browser_info['engine'] = 'WebKit'
        elif 'gecko' in user_agent.lower():
            browser_info['engine'] = 'Gecko'
        elif 'blink' in user_agent.lower():
            browser_info['engine'] = 'Blink'
        
        # Detectar navegador específico
        for key, (pattern, name) in self.browser_patterns.items():
            match = re.search(pattern, user_agent)
            if match:
                browser_info['name'] = name
                browser_info['version'] = match.group(1)
                break
        
        # Detección adicional para Edge
        if 'edg/' in user_agent.lower() and browser_info['name'] == 'Unknown Browser':
            browser_info['name'] = 'Microsoft Edge'
            match = re.search(r'Edg/([\d\.]+)', user_agent)
            if match:
                browser_info['version'] = match.group(1)
        
        return browser_info

    def detect_os(self, user_agent: str) -> Dict[str, str]:
        """Detectar sistema operativo"""
        os_info = {
            'name': 'Unknown OS',
            'version': 'Unknown',
            'architecture': 'Unknown'
        }
        
        for os_type, patterns in self.os_patterns.items():
            for pattern, name in patterns:
                if re.search(pattern, user_agent, re.IGNORECASE):
                    os_info['name'] = name
                    
                    # Extraer versión si es posible
                    version_match = re.search(r'(\d+[\.\_\d]+)', user_agent)
                    if version_match:
                        os_info['version'] = version_match.group(1).replace('_', '.')
                    break
            if os_info['name'] != 'Unknown OS':
                break
        
        # Detectar arquitectura
        if 'x86_64' in user_agent or 'win64' in user_agent.lower():
            os_info['architecture'] = '64-bit'
        elif 'i686' in user_agent or 'i386' in user_agent:
            os_info['architecture'] = '32-bit'
        elif 'arm' in user_agent.lower():
            os_info['architecture'] = 'ARM'
            
        return os_info

    def detect_device(self, user_agent: str) -> Dict[str, str]:
        """Detectar tipo de dispositivo"""
        device_info = {
            'type': 'Desktop',
            'model': 'Unknown',
            'brand': 'Unknown',
            'is_mobile': False,
            'is_tablet': False
        }
        
        ua_lower = user_agent.lower()
        
        # Detectar tipo principal
        if any(keyword in ua_lower for keyword in self.device_types['mobile']):
            device_info['type'] = 'Mobile'
            device_info['is_mobile'] = True
        elif any(keyword in ua_lower for keyword in self.device_types['tablet']):
            device_info['type'] = 'Tablet'
            device_info['is_tablet'] = True
        
        # Detectar marca y modelo específicos
        if 'iphone' in ua_lower:
            device_info['brand'] = 'Apple'
            device_info['model'] = 'iPhone'
        elif 'ipad' in ua_lower:
            device_info['brand'] = 'Apple'
            device_info['model'] = 'iPad'
        elif 'macintosh' in ua_lower:
            device_info['brand'] = 'Apple'
            device_info['model'] = 'Mac'
        elif 'samsung' in ua_lower:
            device_info['brand'] = 'Samsung'
        elif 'huawei' in ua_lower:
            device_info['brand'] = 'Huawei'
        elif 'xiaomi' in ua_lower:
            device_info['brand'] = 'Xiaomi'
        elif 'motorola' in ua_lower:
            device_info['brand'] = 'Motorola'
            
        return device_info

    def detect_network_info(self, ip: str, headers: Dict) -> Dict[str, Any]:
        """Detectar información de red"""
        network_info = {
            'ip_address': ip,
            'type': 'Direct',
            'is_proxy': False,
            'is_vpn': False,
            'country': 'Unknown',
            'threat_level': 'Low'
        }
        
        # Detectar proxies
        proxy_headers = ['x-forwarded-for', 'x-real-ip', 'x-proxy-id', 'via']
        if any(header in headers for header in proxy_headers):
            network_info['is_proxy'] = True
            network_info['type'] = 'Proxy'
            network_info['threat_level'] = 'Medium'
        
        # Detectar IPs locales/VPN
        if ip.startswith(('192.168.', '10.', '172.16.', '169.254.')):
            network_info['is_vpn'] = True
            network_info['type'] = 'VPN/Local'
            network_info['country'] = 'Local Network'
        
        # Detectar TOR (simplificado)
        if '.onion' in str(headers) or 'tor' in str(headers).lower():
            network_info['type'] = 'TOR'
            network_info['threat_level'] = 'High'
            
        return network_info

    def analyze_spider(self, request) -> Dict[str, Any]:
        """Análisis completo de la araña/visitante"""
        user_agent = request.headers.get('User-Agent', '')
        ip = request.remote_addr
        
        browser = self.detect_browser(user_agent)
        os_info = self.detect_os(user_agent)
        device = self.detect_device(user_agent)
        network = self.detect_network_info(ip, dict(request.headers))
        
        # Calcular nivel de amenaza
        threat_score = 0
        if network['is_proxy']:
            threat_score += 1
        if network['is_vpn']:
            threat_score += 1
        if network['type'] == 'TOR':
            threat_score += 2
            
        threat_levels = {0: 'Low', 1: 'Low', 2: 'Medium', 3: 'High'}
        network['threat_level'] = threat_levels.get(threat_score, 'Low')
        
        return {
            'browser': browser,
            'operating_system': os_info,
            'device': device,
            'network': network,
            'user_agent': user_agent,
            'summary': {
                'browser_full': f"{browser['name']} {browser['version']}",
                'os_full': f"{os_info['name']} {os_info['version']}",
                'device_full': f"{device['brand']} {device['model']} ({device['type']})",
                'network_type': network['type'],
                'threat_level': network['threat_level']
            }
        }

# Función de utilidad para usar directamente
def create_spider_profile(request):
    detector = SpiderDetector()
    return detector.analyze_spider(request)