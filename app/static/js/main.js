document.addEventListener('DOMContentLoaded', function() {
    const mapElement = document.getElementById('map');
    if (mapElement) {
        try {
            // Parse events data
            const events = JSON.parse(mapElement.dataset.events || '[]');
            console.log('Found events:', events);
            
            // Initialize map
            const map = L.map('map', {
                center: [52.3676, 4.9041],
                zoom: 7
            });
            
            // Add tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Add markers
            const markers = L.markerClusterGroup();
            const bounds = [];
            
            events.forEach(event => {
                if (event.latitude && event.longitude) {
                    const marker = L.marker([event.latitude, event.longitude]);
                    const popup = `
                        <div class="event-popup">
                            <h5>${event.title}</h5>
                            <p><i class="fas fa-map-marker-alt"></i> ${event.location}</p>
                            <p><i class="fas fa-clock"></i> ${event.start_datetime}</p>
                        </div>
                    `;
                    marker.bindPopup(popup);
                    markers.addLayer(marker);
                    bounds.push([event.latitude, event.longitude]);
                }
            });
            
            map.addLayer(markers);
            
            if (bounds.length > 0) {
                map.fitBounds(bounds);
            }
        } catch (error) {
            console.error('Error initializing map:', error);
        }
    }
    
    // Location suggestions
    const locationInput = document.querySelector('input[name="location_name"]');
    if (locationInput) {
        const container = document.createElement('div');
        container.className = 'suggestions';
        container.style.cssText = `
            position: absolute;
            width: 100%;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            display: none;
            z-index: 1000;
        `;
        locationInput.parentElement.style.position = 'relative';
        locationInput.parentElement.appendChild(container);
        
        let debounceTimer;
        locationInput.addEventListener('input', e => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                const query = e.target.value.trim();
                if (query.length < 3) {
                    container.style.display = 'none';
                    return;
                }
                
                try {
                    const response = await fetch(`/api/location-suggestions?query=${encodeURIComponent(query)}`);
                    const suggestions = await response.json();
                    
                    container.innerHTML = '';
                    suggestions.forEach(suggestion => {
                        const div = document.createElement('div');
                        div.style.cssText = `
                            padding: 8px 12px;
                            cursor: pointer;
                            border-bottom: 1px solid #eee;
                        `;
                        div.textContent = suggestion.address;
                        div.addEventListener('mouseover', () => div.style.backgroundColor = '#f0f0f0');
                        div.addEventListener('mouseout', () => div.style.backgroundColor = 'white');
                        div.addEventListener('click', () => {
                            locationInput.value = suggestion.address;
                            
                            const streetInput = document.querySelector('input[name="street_name"]');
                            if (streetInput && suggestion.street) {
                                streetInput.value = suggestion.street;
                            }
                            
                            const numberInput = document.querySelector('input[name="street_number"]');
                            if (numberInput && suggestion.house_number) {
                                numberInput.value = suggestion.house_number;
                            }
                            
                            const postalInput = document.querySelector('input[name="postal_code"]');
                            if (postalInput && suggestion.postal_code) {
                                postalInput.value = suggestion.postal_code;
                            }
                            
                            container.style.display = 'none';
                        });
                        container.appendChild(div);
                    });
                    
                    container.style.display = suggestions.length ? 'block' : 'none';
                } catch (error) {
                    console.error('Error fetching suggestions:', error);
                    container.style.display = 'none';
                }
            }, 300);
        });
        
        document.addEventListener('click', e => {
            if (!locationInput.contains(e.target) && !container.contains(e.target)) {
                container.style.display = 'none';
            }
        });
    }
});