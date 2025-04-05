document.addEventListener('DOMContentLoaded', () => {
    // Example: Alert user on form submission
    const projectForm = document.querySelector('form[action="/verify_project"]');
    const codeForm = document.querySelector('form[action="/submit_code"]');
    
    if (projectForm) {
        projectForm.addEventListener('submit', () => {
            alert('Project verification form submitted!');
        });
    }
    
    if (codeForm) {
        codeForm.addEventListener('submit', () => {
            alert('Code submission form submitted!');
        });
    }
});
