class SpiderWeb2D {
    constructor() {
        this.width = 800;
        this.height = 600;
        this.center = { x: this.width / 2, y: this.height / 2 };
        
        this.svg = d3.select("#spiderweb")
            .append("svg")
            .attr("width", this.width)
            .attr("height", this.height);
            
        this.simulation = null;
        this.currentData = null;
        
        this.initializeWeb();
        this.loadNetworkData();
        this.loadStats();
        this.loadCurrentVisitor();
        
        // Actualizar cada 3 segundos
        setInterval(() => {
            this.loadNetworkData();
            this.loadStats();
        }, 3000);
    }
    
    initializeWeb() {
        // Fondo de la tela de araña
        this.drawWebBackground();
        
        // Crear simulación de fuerzas
        this.simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-50))
            .force("center", d3.forceCenter(this.center.x, this.center.y))
            .force("collision", d3.forceCollide().radius(d => d.size + 5));
    }
    
    drawWebBackground() {
        // Círculos concéntricos
        const circles = [5, 4, 3, 2, 1];
        circles.forEach(radius => {
            this.svg.append("circle")
                .attr("cx", this.center.x)
                .attr("cy", this.center.y)
                .attr("r", radius * 80)
                .attr("fill", "none")
                .attr("stroke", "rgba(78, 205, 196, 0.2)")
                .attr("stroke-width", 1)
                .attr("stroke-dasharray", "2,2");
        });
        
        // Líneas radiales
        for (let i = 0; i < 12; i++) {
            const angle = (i / 12) * 2 * Math.PI;
            const x = this.center.x + Math.cos(angle) * 400;
            const y = this.center.y + Math.sin(angle) * 400;
            
            this.svg.append("line")
                .attr("x1", this.center.x)
                .attr("y1", this.center.y)
                .attr("x2", x)
                .attr("y2", y)
                .attr("stroke", "rgba(78, 205, 196, 0.1)")
                .attr("stroke-width", 1);
        }
    }
    
    loadNetworkData() {
        fetch('/api/network')
            .then(response => response.json())
            .then(data => {
                this.currentData = data;
                this.updateVisualization(data);
            })
            .catch(error => console.error('Error loading network data:', error));
    }
    
    loadStats() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(stats => {
                document.getElementById('total-visitors').textContent = stats.total_visitors;
                document.getElementById('avg-engagement').textContent = stats.avg_engagement;
                document.getElementById('active-now').textContent = stats.active_now;
                document.getElementById('total-pages').textContent = stats.total_pages;
            })
            .catch(error => console.error('Error loading stats:', error));
    }
    
    loadCurrentVisitor() {
        fetch('/api/visitor/current')
            .then(response => response.json())
            .then(visitor => {
                if (visitor.error) {
                    document.getElementById('current-visitor-info').innerHTML = 
                        '<p style="color: #ccc;">No se pudo cargar la información de tu sesión</p>';
                    return;
                }
                
                document.getElementById('current-visitor-info').innerHTML = `
                    <div style="margin-top: 10px;">
                        <div style="font-size: 0.9em; color: #4ecdc4;">ID: ${visitor.id.slice(0, 12)}...</div>
                        <div style="font-size: 0.8em; margin-top: 5px;">
                            <div>Engagement: <strong>${visitor.engagement_score.toFixed(1)}</strong></div>
                            <div>Páginas: <strong>${visitor.page_visits.length}</strong></div>
                            <div>Tiempo: <strong>${visitor.time_on_site}s</strong></div>
                        </div>
                    </div>
                `;
            })
            .catch(error => {
                document.getElementById('current-visitor-info').innerHTML = 
                    '<p style="color: #ccc;">Error cargando sesión actual</p>';
            });
    }
    
    updateVisualization(data) {
        // Limpiar elementos anteriores
        this.svg.selectAll(".link").remove();
        this.svg.selectAll(".node").remove();
        
        // Crear enlaces
        const link = this.svg.selectAll(".link")
            .data(data.links)
            .enter().append("line")
            .attr("class", "link")
            .attr("stroke", d => this.getLinkColor(d.strength))
            .attr("stroke-width", d => d.strength * 4 + 1)
            .attr("stroke-opacity", 0.6);
        
        // Crear nodos
        const node = this.svg.selectAll(".node")
            .data(data.nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", (event, d) => this.dragStarted(event, d))
                .on("drag", (event, d) => this.dragged(event, d))
                .on("end", (event, d) => this.dragEnded(event, d)));
        
        // Círculos para nodos
        node.append("circle")
            .attr("r", d => d.size)
            .attr("fill", d => this.getNodeColor(d))
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
            .style("cursor", "pointer")
            .on("mouseover", (event, d) => this.showTooltip(event, d))
            .on("mouseout", () => this.hideTooltip())
            .on("click", (event, d) => this.showNodeDetails(d));
        
        // Etiquetas para nodos
        node.append("text")
            .text(d => d.name)
            .attr("text-anchor", "middle")
            .attr("dy", d => -d.size - 8)
            .attr("fill", "#fff")
            .style("font-size", "10px")
            .style("pointer-events", "none")
            .style("font-weight", "bold");
        
        // Actualizar simulación
        this.simulation.nodes(data.nodes);
        this.simulation.force("link").links(data.links);
        this.simulation.alpha(1).restart();
        
        // Actualizar posiciones en cada tick
        this.simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });
    }
    
    getNodeColor(node) {
        if (node.type === 'center') return '#4ecdc4';
        
        // Color basado en engagement score
        const score = node.engagement_score || 0;
        if (score > 50) return '#ff6b6b'; // Alto engagement
        if (score > 20) return '#45b7d1'; // Medio engagement
        return '#96ceb4'; // Bajo engagement
    }
    
    getLinkColor(strength) {
        const intensity = Math.floor(strength * 255);
        return `rgba(78, 205, 196, ${0.3 + strength * 0.7})`;
    }
    
    dragStarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    dragEnded(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    showTooltip(event, d) {
        // Podrías implementar un tooltip aquí si lo deseas
    }
    
    hideTooltip() {
        // Ocultar tooltip
    }
    
    showNodeDetails(node) {
        const detailsDiv = document.getElementById('node-details');
        
        if (node.type === 'center') {
            detailsDiv.innerHTML = `
                <div class="detail-section">
                    <h4>🌐 Sitio Web Central</h4>
                    <div class="detail-item">
                        <span class="detail-label">Visitantes Totales:</span>
                        <span class="detail-value">${this.currentData.nodes.length - 1}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Tipo:</span>
                        <span class="detail-value">Nodo Central</span>
                    </div>
                </div>
            `;
        } else {
            const profile = node.profile;
            const inferred = node.inferred_data;
            
            detailsDiv.innerHTML = `
                <div class="detail-section">
                    <h4>👤 ${node.name}</h4>
                    <div class="detail-item">
                        <span class="detail-label">ID:</span>
                        <span class="detail-value">${node.id.slice(0, 16)}...</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Engagement:</span>
                        <span class="detail-value">${node.engagement_score.toFixed(1)}</span>
                    </div>
                    <div class="engagement-bar">
                        <div class="engagement-fill" style="width: ${node.engagement_score}%"></div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>📊 Comportamiento</h4>
                    <div class="detail-item">
                        <span class="detail-label">Páginas Visitadas:</span>
                        <span class="detail-value">${profile.page_visits.length}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Clicks Realizados:</span>
                        <span class="detail-value">${profile.click_stream.length}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Tiempo en Sitio:</span>
                        <span class="detail-value">${profile.time_on_site}s</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>💻 Información Técnica</h4>
                    <div class="detail-item">
                        <span class="detail-label">Dispositivo:</span>
                        <span class="detail-value">${inferred.device_type}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Navegador:</span>
                        <span class="detail-value">${inferred.browser}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">País:</span>
                        <span class="detail-value">${inferred.country}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Idioma:</span>
                        <span class="detail-value">${inferred.language}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>🎯 Preferencias</h4>
                    <div class="detail-item">
                        <span class="detail-label">Categorías Preferidas:</span>
                        <span class="detail-value">${profile.content_preferences.join(', ')}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Primera Visita:</span>
                        <span class="detail-value">${new Date(profile.first_seen).toLocaleString()}</span>
                    </div>
                </div>
            `;
        }
    }
}

// Funciones globales para los botones
function addDemoVisitor() {
    fetch('/api/visitor/add-demo', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('Visitante demo añadido:', data);
            // Los datos se actualizarán automáticamente en el próximo refresh
        })
        .catch(error => console.error('Error adding demo visitor:', error));
}

function clearDemoVisitors() {
    if (confirm('¿Estás seguro de que quieres eliminar todos los visitantes de demostración?')) {
        fetch('/api/visitors/clear', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log('Visitantes demo eliminados:', data);
                // Los datos se actualizarán automáticamente en el próximo refresh
            })
            .catch(error => console.error('Error clearing demo visitors:', error));
    }
}

function refreshData() {
    if (window.spiderWeb) {
        window.spiderWeb.loadNetworkData();
        window.spiderWeb.loadStats();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.spiderWeb = new SpiderWeb2D();
});