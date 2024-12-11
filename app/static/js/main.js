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
                    fetch(`/api/location-suggestions?query=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            suggestionBox.innerHTML = '';
                            if (data.length > 0) {
                                data.forEach(location => {
                                    const div = document.createElement('div');
                                    div.className = 'location-suggestion-item';
                                    div.textContent = location.address;
                                    div.addEventListener('click', () => {
                                        document.querySelector('[name="location_name"]').value = location.address;
                                        if (location.street) {
                                            document.querySelector('[name="street_name"]').value = location.street;
                                        }
                                        if (location.house_number) {
                                            document.querySelector('[name="street_number"]').value = location.house_number;
                                        }
                                        if (location.postal_code) {
                                            document.querySelector('[name="postal_code"]').value = location.postal_code;
                                        }
                                        suggestionBox.style.display = 'none';
                                    });
                                    suggestionBox.appendChild(div);
                                });
                                suggestionBox.style.display = 'block';
                            } else {
                                suggestionBox.style.display = 'none';
                            }
                        })
                        .catch(error => {
                            console.error('Error fetching location suggestions:', error);
                            suggestionBox.style.display = 'none';
                        });
                } else {
                    suggestionBox.style.display = 'none';
                }
            }, 300);
        });
        
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && !suggestionBox.contains(e.target)) {
                suggestionBox.style.display = 'none';
            }
        });
    });

    // Map initialization
    if (document.getElementById('map')) {
        // Initialize the map with clustering support
        const map = L.map('map').setView([52.3676, 4.9041], 7);  // Default to Netherlands
        
        // Add the base map layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Add scale control
        L.control.scale().addTo(map);

        // Create a marker cluster group
        const markers = L.markerClusterGroup({
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: true,
            zoomToBoundsOnClick: true
        });

        // Custom popup style
        const popupOptions = {
            maxWidth: 300,
            className: 'custom-popup'
        };

        // Add markers for events with coordinates
        if (typeof eventLocations !== 'undefined' && eventLocations.length > 0) {
            const bounds = [];
            
            eventLocations.forEach(event => {
                if (event.latitude && event.longitude) {
                    const coords = [event.latitude, event.longitude];
                    bounds.push(coords);

                    // Create marker with custom icon
                    const marker = L.marker(coords, {
                        title: event.title,
                        riseOnHover: true
                    });

                    // Create popup content
                    const popupContent = `
                        <div class="event-popup">
                            <h5>${event.title}</h5>
                            <p><i class="fas fa-map-marker-alt"></i> ${event.location}</p>
                            <p><i class="fas fa-clock"></i> ${event.start}</p>
                        </div>
                    `;

                    marker.bindPopup(popupContent, popupOptions);
                    markers.addLayer(marker);
                }
            });

            // Add the marker cluster group to the map
            map.addLayer(markers);

            // Fit map to show all markers if there are any
            if (bounds.length > 0) {
                const padded = L.latLngBounds(bounds).pad(0.1);  // Add 10% padding
                map.fitBounds(padded);
            }
        }

        // Add fullscreen control
        map.addControl(new L.Control.Fullscreen());

        // Add locate control
        L.control.locate({
            position: 'topleft',
            strings: {
                title: 'Show me where I am'
            }
        }).addTo(map);
    }
});
