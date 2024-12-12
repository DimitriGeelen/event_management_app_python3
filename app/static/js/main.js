document.addEventListener('DOMContentLoaded', function() {
    // Location suggestions functionality
    const locationInput = document.querySelector('input[name="location_name"]');
    const streetInput = document.querySelector('input[name="street_name"]');
    const streetNumberInput = document.querySelector('input[name="street_number"]');
    const postalCodeInput = document.querySelector('input[name="postal_code"]');
    
    if (locationInput) {
        // Create suggestion container
        const suggestionContainer = document.createElement('div');
        suggestionContainer.className = 'suggestion-container';
        suggestionContainer.style.cssText = `
            position: absolute;
            max-height: 200px;
            overflow-y: auto;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: none;
            z-index: 1000;
            width: 100%;
        `;
        locationInput.parentElement.style.position = 'relative';
        locationInput.parentElement.appendChild(suggestionContainer);

        // Add input event listener
        let timeoutId = null;
        locationInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            
            // Clear previous timeout
            if (timeoutId) {
                clearTimeout(timeoutId);
            }

            // Set new timeout to prevent too many requests
            timeoutId = setTimeout(async () => {
                if (query.length < 3) {
                    suggestionContainer.style.display = 'none';
                    return;
                }

                try {
                    console.log('Fetching suggestions for:', query);
                    const response = await fetch(`/api/location-suggestions?query=${encodeURIComponent(query)}`);
                    if (!response.ok) throw new Error('Network response was not ok');
                    const suggestions = await response.json();
                    console.log('Received suggestions:', suggestions);

                    // Clear previous suggestions
                    suggestionContainer.innerHTML = '';

                    if (suggestions.length > 0) {
                        suggestions.forEach(suggestion => {
                            const div = document.createElement('div');
                            div.className = 'suggestion-item';
                            div.style.cssText = `
                                padding: 8px 12px;
                                cursor: pointer;
                                border-bottom: 1px solid #eee;
                            `;
                            div.textContent = suggestion.address;
                            div.addEventListener('mouseover', () => {
                                div.style.backgroundColor = '#f0f0f0';
                            });
                            div.addEventListener('mouseout', () => {
                                div.style.backgroundColor = 'white';
                            });
                            div.addEventListener('click', () => {
                                locationInput.value = suggestion.address;
                                if (streetInput && suggestion.street) {
                                    streetInput.value = suggestion.street;
                                }
                                if (streetNumberInput && suggestion.house_number) {
                                    streetNumberInput.value = suggestion.house_number;
                                }
                                if (postalCodeInput && suggestion.postal_code) {
                                    postalCodeInput.value = suggestion.postal_code;
                                }
                                suggestionContainer.style.display = 'none';
                            });
                            suggestionContainer.appendChild(div);
                        });
                        suggestionContainer.style.display = 'block';
                    } else {
                        suggestionContainer.style.display = 'none';
                    }
                } catch (error) {
                    console.error('Error fetching suggestions:', error);
                    suggestionContainer.style.display = 'none';
                }
            }, 300); // 300ms delay
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!locationInput.contains(e.target) && !suggestionContainer.contains(e.target)) {
                suggestionContainer.style.display = 'none';
            }
        });
    }

    // Map initialization code
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
            spiderfyOnMaxZoom: true,
            disableClusteringAtZoom: 19
        });

        // Add markers for events with coordinates
        if (typeof eventLocations !== 'undefined' && eventLocations.length > 0) {
            console.log('Found event locations:', eventLocations);
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
                                    width: 12px; 
                                    height: 12px; 
                                    border-radius: 50%; 
                                    border: 2px solid #fff;
                                    box-shadow: 0 0 4px rgba(0,0,0,0.3);"></div>`,
                        iconSize: [12, 12],
                        iconAnchor: [6, 6]
                    });

                    // Create popup content
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
                console.log('Fitting bounds to markers:', bounds);
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
