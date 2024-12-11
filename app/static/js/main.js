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
        const map = L.map('map').setView([52.3676, 4.9041], 7);  // Default to Netherlands
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Add markers for each event
        if (typeof eventLocations !== 'undefined' && eventLocations.length > 0) {
            const markers = [];
            const geocodePromises = eventLocations.map(event => {
                return fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(event.location)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data && data.length > 0) {
                            const marker = L.marker([data[0].lat, data[0].lon])
                                .bindPopup(`
                                    <strong>${event.title}</strong><br>
                                    ${event.location}<br>
                                    <em>Starts: ${event.start}</em>
                                `)
                                .addTo(map);
                            markers.push(marker);
                            return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
                        }
                    })
                    .catch(error => console.error('Error geocoding:', error));
            });

            // After all markers are added, fit the map to show all markers
            Promise.all(geocodePromises).then(coordinates => {
                const validCoordinates = coordinates.filter(coord => coord);
                if (validCoordinates.length > 0) {
                    const bounds = L.latLngBounds(validCoordinates);
                    map.fitBounds(bounds, { padding: [50, 50] });
                }
            });
        }
    }
});
