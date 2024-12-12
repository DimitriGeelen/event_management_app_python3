document.addEventListener('DOMContentLoaded', function() {
    // Initialize map if it exists on the page
    const mapElement = document.getElementById('map');
    if (mapElement) {
        console.log('Initializing map...');

        // Initialize the map with default view of Netherlands
        const map = L.map('map', {
            center: [52.3676, 4.9041], // Amsterdam coordinates
            zoom: 7,
            minZoom: 3
        });

        // Add the OpenStreetMap layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        // Create a marker cluster group with custom options
        const markers = L.markerClusterGroup({
            showCoverageOnHover: false,
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true
        });

        // Add markers for events with coordinates
        if (typeof eventLocations !== 'undefined' && eventLocations.length > 0) {
            console.log('Available event locations:', eventLocations);
            const bounds = [];

            eventLocations.forEach(event => {
                // Convert coordinates to float and validate
                const lat = parseFloat(event.latitude);
                const lon = parseFloat(event.longitude);

                console.log(`Processing event: ${event.title}`);
                console.log(`Raw coordinates: lat=${event.latitude}, lon=${event.longitude}`);
                console.log(`Parsed coordinates: lat=${lat}, lon=${lon}`);

                if (!isNaN(lat) && !isNaN(lon) && 
                    lat >= -90 && lat <= 90 && 
                    lon >= -180 && lon <= 180) {
                    
                    console.log(`Adding marker for "${event.title}" at [${lat}, ${lon}]`);
                    
                    // Create custom icon
                    const eventIcon = L.divIcon({
                        className: 'custom-div-icon',
                        html: `<div style="background-color: #3498db; 
                                    width: 10px; 
                                    height: 10px; 
                                    border-radius: 50%; 
                                    border: 2px solid #fff;
                                    box-shadow: 0 0 4px rgba(0,0,0,0.3);">
                            </div>`,
                        iconSize: [10, 10],
                        iconAnchor: [5, 5]
                    });

                    // Create popup content with sanitized HTML
                    const popupContent = `
                        <div class="event-popup">
                            <h5>${escapeHtml(event.title)}</h5>
                            <p><i class="fas fa-map-marker-alt"></i> ${escapeHtml(event.location)}</p>
                            <p><i class="fas fa-clock"></i> ${escapeHtml(event.start)}</p>
                        </div>
                    `;

                    // Create and add marker
                    const marker = L.marker([lat, lon], {icon: eventIcon})
                        .bindPopup(popupContent, {
                            maxWidth: 300,
                            minWidth: 200,
                            autoPan: true,
                            closeButton: true,
                            closeOnClick: false
                        });
                    
                    markers.addLayer(marker);
                    bounds.push([lat, lon]);
                    console.log(`Successfully added marker for "${event.title}"`);
                } else {
                    console.warn(`Invalid coordinates for event: ${event.title}`);
                }
            });

            // Add the marker cluster group to the map
            map.addLayer(markers);
            console.log(`Added marker cluster group with ${bounds.length} markers`);

            // Fit bounds if we have any valid markers
            if (bounds.length > 0) {
                console.log(`Fitting bounds to ${bounds.length} markers:`, bounds);
                map.fitBounds(bounds, { 
                    padding: [50, 50],
                    maxZoom: 13 // Prevent too much zoom when single/few markers
                });
            } else {
                console.warn('No valid markers to fit bounds');
            }
        } else {
            console.log('No event locations found in eventLocations variable');
        }
    } else {
        console.log('Map element not found on page');
    }
});

// Helper function to escape HTML and prevent XSS
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}