document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('family-members-container');
    const template = document.getElementById('family-member-template');
    let memberCount = 0;

    function addFamilyMember() {
        if (memberCount >= 5) return;

        const clone = template.content.cloneNode(true);
        const form = clone.querySelector('.family-member-form');
        
        // Update member number
        clone.querySelector('.member-number').textContent = `Μέλος ${memberCount + 1}`;
        
        // Update field names
        const inputs = clone.querySelectorAll('input');
        inputs.forEach(input => {
            const name = input.getAttribute('name');
            if (name) {
                input.setAttribute('name', name.replace('[index]', `[${memberCount}]`));
            }
        });

        // Only show add button on the last member
        const addButtons = container.querySelectorAll('.add-family-member');
        addButtons.forEach(btn => btn.style.display = 'none');
        
        const addButton = clone.querySelector('.add-family-member');
        if (memberCount < 4) {
            addButton.style.display = 'block';
            addButton.addEventListener('click', addFamilyMember);
        } else {
            addButton.style.display = 'none';
        }

        container.appendChild(clone);
        memberCount++;
    }

    // Add first member automatically
    addFamilyMember();
}); 