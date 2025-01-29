document.addEventListener('DOMContentLoaded', function() {
    const emailsContainer = document.querySelector('.dynamic-emails-container');
    
    if (emailsContainer) {
        const addButton = emailsContainer.querySelector('.add-email');
        const emailFields = emailsContainer.querySelector('.email-fields');

        // Add new email field
        addButton.addEventListener('click', function() {
            const newGroup = document.createElement('div');
            newGroup.className = 'email-field-group mb-2';
            newGroup.innerHTML = `
                <div class="input-group">
                    <input type="email" 
                           name="guardian_emails[]" 
                           class="form-control"
                           placeholder="Εισάγετε email">
                    <button type="button" class="btn btn-danger remove-email">
                        <i class="bi bi-dash-circle"></i>
                    </button>
                </div>
            `;
            emailFields.appendChild(newGroup);
        });

        // Remove email field
        emailFields.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-email') || 
                e.target.closest('.remove-email')) {
                const group = e.target.closest('.email-field-group');
                if (emailFields.children.length > 1) {  // Keep at least one field
                    group.remove();
                }
            }
        });
    }
}); 