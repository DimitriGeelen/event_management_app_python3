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
            }, 300);
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
        console.log('Initializing map...');

        // Initialize the map
        const map = L.map('map').setView([52.3676, 4.9041], 7);

        // Add the base map layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        // Check if we have event locations
        if (typeof eventLocations !== 'undefined') {
            console.log('Event locations found:', eventLocations);
            
            const markers = L.markerClusterGroup();
            const bounds = [];

            eventLocations.forEach(event => {
                console.log('Processing event:', event);
                
                if (event.latitude && event.longitude) {
                    console.log(`Adding marker at ${event.latitude}, ${event.longitude}`);
                    
                    const popupContent = `
                        <div class="event-popup">
                            <h5>${event.title}</h5>
                            <p><i class="fas fa-map-marker-alt"></i> ${event.location}</p>
                            <p><i class="fas fa-clock"></i> ${event.start}</p>
                        </div>
                    `;

                    const marker = L.marker([parseFloat(event.latitude), parseFloat(event.longitude)])
                        .bindPopup(popupContent);
                    
                    markers.addLayer(marker);
                    bounds.push([event.latitude, event.longitude]);
                }
            });

            // Add markers to map
            map.addLayer(markers);

            // Fit bounds if we have any markers
            if (bounds.length > 0) {
                console.log('Fitting bounds to markers');
                map.fitBounds(bounds, { padding: [50, 50] });
            } else {
                console.log('No valid markers found');
            }
        } else {
            console.log('No event locations data found');
        }

        // Add map controls
        map.addControl(new L.Control.Fullscreen());
        
        L.control.locate({
            position: 'topleft',
            strings: {
                title: 'Show my location'
            }
        }).addTo(map);
    } else {
        console.log('Map element not found');
    }
});
