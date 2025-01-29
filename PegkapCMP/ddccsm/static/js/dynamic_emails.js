document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('#additional-emails');
    const addButton = document.querySelector('.add-email-field');
    let emailCount = document.querySelectorAll('.guardian-email-field').length;

    addButton.addEventListener('click', function() {
        emailCount++;
        const newField = document.createElement('div');
        newField.className = 'guardian-email-field mb-3';
        newField.innerHTML = `
            <div class="input-group">
                <input type="email" 
                       name="guardian_email_${emailCount}" 
                       class="form-control" 
                       placeholder="Email δικαστικού συμπαραστάτη">
                <button type="button" class="btn btn-danger remove-email">
                    <i class="fas fa-minus"></i>
                </button>
            </div>
        `;
        container.appendChild(newField);
    });

    // Event delegation for remove buttons
    container.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-email') || 
            e.target.parentElement.classList.contains('remove-email')) {
            const fieldDiv = e.target.closest('.guardian-email-field');
            fieldDiv.remove();
        }
    });
}); 