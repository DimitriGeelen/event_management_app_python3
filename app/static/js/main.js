document.addEventListener('DOMContentLoaded', function() {
    // Location suggestions handling
    // ... (previous location suggestions code remains the same)

    // Initialize map if it exists on the page
    const mapElement = document.getElementById('map');
    if (mapElement) {
        console.log('Initializing map...');

        // Initialize the map
        const map = L.map('map', {
            center: [52.3676, 4.9041],
            zoom: 7
        });

        // Add the base map layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        // Create a marker cluster group
        const markers = L.markerClusterGroup();

        // Add markers for all events with coordinates
        if (typeof eventLocations !== 'undefined' && eventLocations.length > 0) {
            console.log('Found event locations:', eventLocations);
            const bounds = [];

            eventLocations.forEach(event => {
                // Convert coordinates to float
                const lat = parseFloat(event.latitude);
                const lon = parseFloat(event.longitude);

                console.log(`Processing event: ${event.title}, coords: [${lat}, ${lon}]`);

                if (!isNaN(lat) && !isNaN(lon)) {
                    console.log(`Adding marker for ${event.title} at [${lat}, ${lon}]`);
                    
                    // Create popup content
                    const popupContent = `
                        <div class="event-popup">
                            <h5>${event.title}</h5>
                            <p><i class="fas fa-map-marker-alt"></i> ${event.location}</p>
                            <p><i class="fas fa-clock"></i> ${event.start}</p>
                        </div>
                    `;

                    // Create and add marker
                    const marker = L.marker([lat, lon])
                        .bindPopup(popupContent);
                    
                    markers.addLayer(marker);
                    bounds.push([lat, lon]);
                } else {
                    console.warn(`Invalid coordinates for event: ${event.title}`);
                }
            });

            // Add the marker cluster group to the map
            map.addLayer(markers);

            // Fit bounds if we have any markers
            if (bounds.length > 0) {
                console.log(`Fitting bounds to ${bounds.length} markers`);
                map.fitBounds(bounds, { padding: [50, 50] });
            } else {
                console.warn('No valid markers to fit bounds');
            }
        } else {
            console.warn('No event locations found');
        }
    }
});
