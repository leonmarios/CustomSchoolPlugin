document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('family-members');
    const addButton = document.getElementById('add-member');
    let memberCount = container.children.length;

    addButton.addEventListener('click', function() {
        memberCount++;
        const template = document.querySelector('.family-member-form').cloneNode(true);
        template.querySelector('h6').textContent = `Μέλος ${memberCount}`;
        
        // Clear all input values
        template.querySelectorAll('input, textarea').forEach(input => {
            input.value = '';
            // Update the input names to use the new index
            input.name = input.name.replace(/\d+/, memberCount);
            input.id = input.id.replace(/\d+/, memberCount);
        });

        // Update labels' for attributes
        template.querySelectorAll('label').forEach(label => {
            if (label.htmlFor) {
                label.htmlFor = label.htmlFor.replace(/\d+/, memberCount);
            }
        });

        container.appendChild(template);
    });

    // Event delegation for remove buttons
    container.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-member') || 
            e.target.parentElement.classList.contains('remove-member')) {
            const memberForm = e.target.closest('.family-member-form');
            if (container.children.length > 1) {
                memberForm.remove();
                // Update the numbering
                container.querySelectorAll('.family-member-form h6').forEach((header, index) => {
                    header.textContent = `Μέλος ${index + 1}`;
                });
                memberCount--;
            }
        }
    });
}); 