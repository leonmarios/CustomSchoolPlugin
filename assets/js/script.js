document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tabs a');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', function (e) {
            e.preventDefault();

            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            this.classList.add('active');
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.classList.add('active');
        });
    });

    // Automatically activate the first tab
    if (tabs.length > 0) {
        tabs[0].classList.add('active');
        contents[0].classList.add('active');
    }
});
