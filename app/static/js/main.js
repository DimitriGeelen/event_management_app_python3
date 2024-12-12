document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    setupLocationSuggestions();
});

function initializeMap() {
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.log('Map element not found');
        return;
    }

    console.log('Initializing map...');

    try {
        // Get event data from data attribute
        const eventData = JSON.parse(mapElement.dataset.events || '[]');
        console.log('Loaded event data:', eventData);

        // Initialize the map
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

        // Create marker cluster group
        const markers = L.markerClusterGroup({
            showCoverageOnHover: false,
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true
        });

        // Add markers for events with coordinates
        const bounds = [];
        eventData.forEach(event => {
            if (event.latitude && event.longitude) {
                const lat = parseFloat(event.latitude);
                const lon = parseFloat(event.longitude);

                if (!isNaN(lat) && !isNaN(lon) && 
                    lat >= -90 && lat <= 90 && 
                    lon >= -180 && lon <= 180) {
                    
                    console.log(`Adding marker for "${event.title}" at [${lat}, ${lon}]`);
                    
                    // Create marker
                    const marker = L.marker([lat, lon]);
                    
                    // Create popup content
                    const popupContent = `
                        <div class="event-popup">
                            <h5>${escapeHtml(event.title)}</h5>
                            ${event.location ? `<p><i class="fas fa-map-marker-alt"></i> ${escapeHtml(event.location)}</p>` : ''}
                            <p><i class="fas fa-clock"></i> ${escapeHtml(event.start_datetime)}</p>
                        </div>
                    `;

                    // Bind popup to marker
                    marker.bindPopup(popupContent, {
                        maxWidth: 300,
                        minWidth: 200
                    });
                    
                    // Add marker to cluster group
                    markers.addLayer(marker);
                    bounds.push([lat, lon]);
                }
            }
        });

        // Add markers to map
        map.addLayer(markers);

        // Fit bounds if we have markers
        if (bounds.length > 0) {
            console.log(`Fitting bounds to ${bounds.length} markers`);
            map.fitBounds(bounds, { 
                padding: [50, 50],
                maxZoom: 13
            });
        } else {
            console.log('No valid markers to fit bounds');
        }
    } catch (error) {
        console.error('Error initializing map:', error);
    }
}

function setupLocationSuggestions() {
    const locationInput = document.querySelector('input[name="location_name"]');
    if (!locationInput) return;

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

    // Handle input with debounce
    let timeoutId = null;
    locationInput.addEventListener('input', function(e) {
        if (timeoutId) clearTimeout(timeoutId);
        
        timeoutId = setTimeout(async () => {
            const query = e.target.value.trim();
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
                displaySuggestions(suggestions);
            } catch (error) {
                console.error('Error fetching suggestions:', error);
                suggestionContainer.style.display = 'none';
            }
        }, 300);
    });

    // Handle suggestion display
    function displaySuggestions(suggestions) {
        suggestionContainer.innerHTML = '';
        
        if (suggestions.length === 0) {
            suggestionContainer.style.display = 'none';
            return;
        }

        suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.style.cssText = `
                padding: 8px 12px;
                cursor: pointer;
                border-bottom: 1px solid #eee;
            `;
            div.textContent = suggestion.address;
            
            div.addEventListener('mouseover', () => div.style.backgroundColor = '#f0f0f0');
            div.addEventListener('mouseout', () => div.style.backgroundColor = 'white');
            
            div.addEventListener('click', () => {
                fillLocationFields(suggestion);
                suggestionContainer.style.display = 'none';
            });

            suggestionContainer.appendChild(div);
        });

        suggestionContainer.style.display = 'block';
    }

    // Fill form fields with selected suggestion
    function fillLocationFields(suggestion) {
        const streetInput = document.querySelector('input[name="street_name"]');
        const streetNumberInput = document.querySelector('input[name="street_number"]');
        const postalCodeInput = document.querySelector('input[name="postal_code"]');

        locationInput.value = suggestion.address;
        if (streetInput && suggestion.street) streetInput.value = suggestion.street;
        if (streetNumberInput && suggestion.house_number) streetNumberInput.value = suggestion.house_number;
        if (postalCodeInput && suggestion.postal_code) postalCodeInput.value = suggestion.postal_code;
    }

    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!locationInput.contains(e.target) && !suggestionContainer.contains(e.target)) {
            suggestionContainer.style.display = 'none';
        }
    });
}

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
