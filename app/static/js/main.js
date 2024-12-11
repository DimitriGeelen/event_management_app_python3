document.addEventListener('DOMContentLoaded', function() {
    // Location suggestions handling
    const locationInputs = document.querySelectorAll('.location-input');
    
    locationInputs.forEach(input => {
        let suggestionBox = document.createElement('div');
        suggestionBox.className = 'location-suggestions';
        suggestionBox.style.display = 'none';
        input.parentNode.appendChild(suggestionBox);
        
        let debounceTimer;
        
        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 3) {
                    // Show loading indicator
                    suggestionBox.innerHTML = '<div class="p-2">Loading...</div>';
                    suggestionBox.style.display = 'block';
                    
                    fetch(`/api/location-suggestions?query=${encodeURIComponent(query)}`)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            // Check if there's an error message
                            if (data.error) {
                                throw new Error(data.error);
                            }
                            
                            suggestionBox.innerHTML = '';
                            if (data.length > 0) {
                                data.forEach(location => {
                                    const div = document.createElement('div');
                                    div.className = 'location-suggestion-item';
                                    div.textContent = location.address;
                                    div.addEventListener('click', () => {
                                        // Fill in all the address fields
                                        const formElements = {
                                            'location_name': location.address,
                                            'street_name': location.street || '',
                                            'street_number': location.house_number || '',
                                            'postal_code': location.postal_code || ''
                                        };
                                        
                                        // Update each form field if it exists
                                        Object.entries(formElements).forEach(([fieldName, value]) => {
                                            const field = document.querySelector(`[name="${fieldName}"]`);
                                            if (field) {
                                                field.value = value;
                                            }
                                        });
                                        
                                        suggestionBox.style.display = 'none';
                                    });
                                    suggestionBox.appendChild(div);
                                });
                                suggestionBox.style.display = 'block';
                            } else {
                                suggestionBox.innerHTML = '<div class="p-2">No results found</div>';
                                suggestionBox.style.display = 'block';
                            }
                        })
                        .catch(error => {
                            console.error('Error fetching location suggestions:', error);
                            suggestionBox.innerHTML = '<div class="p-2 text-danger">Error fetching suggestions</div>';
                            suggestionBox.style.display = 'block';
                        });
                } else {
                    suggestionBox.style.display = 'none';
                }
            }, 500); // Increased debounce time to 500ms
        });
        
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && !suggestionBox.contains(e.target)) {
                suggestionBox.style.display = 'none';
            }
        });
    });

    // Initialize map if it exists on the page
    const mapElement = document.getElementById('map');
    if (mapElement) {
        // Initialize the map with Netherlands center
        const map = L.map('map').setView([52.3676, 4.9041], 7);
        
        // Add the OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Create a marker cluster group
        const markers = L.markerClusterGroup();

        // Add markers for all events with coordinates
        if (typeof eventLocations !== 'undefined' && eventLocations.length > 0) {
            const bounds = [];
            eventLocations.forEach(event => {
                if (event.latitude && event.longitude) {
                    const marker = L.marker([event.latitude, event.longitude])
                        .bindPopup(`
                            <div class="event-popup">
                                <h5>${event.title}</h5>
                                <p><i class="fas fa-tag"></i> ${event.category}</p>
                                <p><i class="fas fa-map-marker-alt"></i> ${event.location}</p>
                                <p><i class="fas fa-clock"></i> ${event.start}</p>
                            </div>
                        `);
                    markers.addLayer(marker);
                    bounds.push([event.latitude, event.longitude]);
                }
            });

            // Add the marker cluster group to the map
            map.addLayer(markers);

            // Fit the map to show all markers if there are any
            if (bounds.length > 0) {
                map.fitBounds(bounds, { padding: [50, 50] });
            }
        }

        // Add fullscreen control
        map.addControl(new L.Control.Fullscreen());

        // Add locate control
        L.control.locate({
            position: 'topleft',
            strings: {
                title: 'Show me where I am'
            },
            locateOptions: {
                maxZoom: 15
            }
        }).addTo(map);

        // Add scale control
        L.control.scale().addTo(map);
    }
});
