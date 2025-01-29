document.addEventListener('DOMContentLoaded', function() {
    const disabilitySelect = document.querySelector('[name="disability_percentage"]');
    const otherPercentageField = document.querySelector('#div_id_other_disability_percentage');

    function toggleOtherPercentage() {
        if (disabilitySelect && otherPercentageField) {
            if (disabilitySelect.value === 'other') {
                otherPercentageField.style.display = 'block';
            } else {
                otherPercentageField.style.display = 'none';
                // Clear the other percentage field when hidden
                const otherInput = otherPercentageField.querySelector('input');
                if (otherInput) otherInput.value = '';
            }
        }
    }

    if (disabilitySelect) {
        // Initial state
        toggleOtherPercentage();
        
        // On change
        disabilitySelect.addEventListener('change', toggleOtherPercentage);
    }
}); 