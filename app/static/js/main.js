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
        if (typeof window.eventLocations !== 'undefined' && window.eventLocations.length > 0) {
            console.log('Found event locations:', window.eventLocations);
            const bounds = [];

            window.eventLocations.forEach(event => {
                // Convert coordinates to float and validate
                const lat = parseFloat(event.latitude);
                const lon = parseFloat(event.longitude);

                if (!isNaN(lat) && !isNaN(lon) && 
                    lat >= -90 && lat <= 90 && 
                    lon >= -180 && lon <= 180) {
                    
                    // Create marker
                    const marker = L.marker([lat, lon]);
                    
                    // Create popup content
                    const popupContent = `
                        <div class="event-popup">
                            <h5>${escapeHtml(event.title)}</h5>
                            ${event.location ? `<p><i class="fas fa-map-marker-alt"></i> ${escapeHtml(event.location)}</p>` : ''}
                            ${event.start ? `<p><i class="fas fa-clock"></i> ${escapeHtml(event.start)}</p>` : ''}
                        </div>
                    `;

                    // Bind popup to marker
                    marker.bindPopup(popupContent);
                    
                    // Add marker to cluster group
                    markers.addLayer(marker);
                    
                    // Add coordinates to bounds
                    bounds.push([lat, lon]);
                }
            });

            // Add the marker cluster group to the map
            map.addLayer(markers);

            // Fit bounds if we have any valid markers
            if (bounds.length > 0) {
                map.fitBounds(bounds, { 
                    padding: [50, 50],
                    maxZoom: 13
                });
            }
        }
    }

    // Location suggestions functionality
    const locationInput = document.querySelector('input[name="location_name"]');
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

        // Add input event listener with debounce
        let timeoutId = null;
        locationInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            
            // Clear previous timeout
            if (timeoutId) {
                clearTimeout(timeoutId);
            }

            // Set new timeout
            timeoutId = setTimeout(async () => {
                if (query.length < 3) {
                    suggestionContainer.style.display = 'none';
                    return;
                }

                try {
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
                            
                            // Add hover effect
                            div.addEventListener('mouseover', () => {
                                div.style.backgroundColor = '#f0f0f0';
                            });
                            div.addEventListener('mouseout', () => {
                                div.style.backgroundColor = 'white';
                            });
                            
                            // Handle click
                            div.addEventListener('click', () => {
                                // Fill in the form fields
                                const streetInput = document.querySelector('input[name="street_name"]');
                                const streetNumberInput = document.querySelector('input[name="street_number"]');
                                const postalCodeInput = document.querySelector('input[name="postal_code"]');

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

                                // Hide suggestions
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