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
        // Map initialization code...
    }
});
