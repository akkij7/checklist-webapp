// Add custom JavaScript here 

// Main JavaScript for ChecklistPro

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    // Flash message auto-dismiss after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const closeBtn = message.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        console.log('Found form:', form.id || 'unnamed form');
        const requiredInputs = form.querySelectorAll('[required]');
        requiredInputs.forEach(input => {
            input.addEventListener('invalid', function(e) {
                input.classList.add('is-invalid');
            });
            input.addEventListener('input', function(e) {
                if (input.validity.valid) {
                    input.classList.remove('is-invalid');
                }
            });
        });
    });

    // *** DISABLED: No longer intercepting form submission ***
    // Comment out the intercepting form submission code to allow normal form submission
    /*
    const createForm = document.getElementById('createChecklistForm');
    if (createForm) {
        console.log('Found create checklist form');
        
        // Test event listener
        document.getElementById('createBtn').addEventListener('click', function(event) {
            console.log('Create button clicked directly');
        });
        
        createForm.addEventListener('submit', function(e) {
            console.log('Form submission intercepted');
            
            // Get the form data
            const nameInput = document.getElementById('checklist_name');
            const itemsInput = document.getElementById('checklist_items');
            
            if (!nameInput || !nameInput.value.trim()) {
                console.error('Checklist name is empty!');
                // We'll let the default validation handle this
                return;
            }
            
            console.log('Form data:', {
                name: nameInput.value,
                items: itemsInput ? itemsInput.value : '(none)'
            });
            
            // Prevent default form submission
            e.preventDefault();
            console.log('Default form submission prevented');
            
            // Create a direct form submission as backup
            const formData = new FormData();
            formData.append('checklist_name', nameInput.value);
            formData.append('checklist_items', itemsInput ? itemsInput.value : '');
            
            // Show loading state
            const submitBtn = document.getElementById('createBtn');
            const originalBtnContent = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...';
            
            console.log('Attempting AJAX POST to /create_ajax');
            
            // Make AJAX request
            fetch('/create_ajax', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    checklist_name: nameInput.value,
                    checklist_items: itemsInput ? itemsInput.value : ''
                })
            })
            .then(response => {
                console.log('AJAX response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('AJAX response data:', data);
                
                if (data.status === 'success') {
                    // Show success message
                    const successMsg = document.createElement('div');
                    successMsg.className = 'alert alert-success mt-3';
                    successMsg.innerHTML = data.message;
                    createForm.appendChild(successMsg);
                    
                    // Redirect after a short delay
                    setTimeout(() => {
                        console.log('Redirecting to:', data.redirect);
                        window.location.href = data.redirect;
                    }, 1000);
                } else {
                    // Show error message
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'alert alert-danger mt-3';
                    errorMsg.innerHTML = `Error: ${data.message}`;
                    createForm.appendChild(errorMsg);
                    
                    // Reset button
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnContent;
                }
            })
            .catch(error => {
                console.error('AJAX Error:', error);
                
                // Fallback to traditional form submission
                console.log('Falling back to traditional form submission');
                
                // Create a hidden form for direct submission
                const hiddenForm = document.createElement('form');
                hiddenForm.method = 'POST';
                hiddenForm.action = '/create';
                hiddenForm.style.display = 'none';
                
                // Add inputs
                const nameField = document.createElement('input');
                nameField.type = 'text';
                nameField.name = 'checklist_name';
                nameField.value = nameInput.value;
                hiddenForm.appendChild(nameField);
                
                const itemsField = document.createElement('textarea');
                itemsField.name = 'checklist_items';
                itemsField.value = itemsInput ? itemsInput.value : '';
                hiddenForm.appendChild(itemsField);
                
                // Add form to document and submit
                document.body.appendChild(hiddenForm);
                hiddenForm.submit();
            });
        });
    } else {
        console.warn('Create checklist form not found!');
    }
    */
    
    // Textarea auto-resize
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Create button loading state - DISABLED to prevent conflicts
    /*
    const submitBtns = document.querySelectorAll('button[type="submit"]');
    submitBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            console.log('Submit button clicked:', btn.id || 'unnamed button');
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                const originalContent = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                this.disabled = true;
                
                // Re-enable after 5s in case the form submission fails
                setTimeout(() => {
                    this.innerHTML = originalContent;
                    this.disabled = false;
                }, 5000);
            }
        });
    });
    */

    // Add keyboard shortcuts: Press 'c' to focus on create checklist name field on homepage
    document.addEventListener('keydown', function(e) {
        if (e.key === 'c' && !e.ctrlKey && !e.metaKey && document.getElementById('checklist_name')) {
            const activeElement = document.activeElement;
            // Don't trigger when in input/textarea
            if (activeElement.tagName !== 'INPUT' && activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                document.getElementById('checklist_name').focus();
            }
        }
    });

    // Add visual feedback to checkbox clicks
    const checkboxes = document.querySelectorAll('.item-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const listItem = this.closest('.checklist-item');
            if (this.checked) {
                listItem.classList.add('completed');
                listItem.classList.add('pulse-animation');
                setTimeout(() => {
                    listItem.classList.remove('pulse-animation');
                }, 500);
            } else {
                listItem.classList.remove('completed');
            }
        });
    });
    
    // Initialize Bootstrap tooltips if Bootstrap is defined
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add a simple fallback for the main form in case of issues with other scripts
    const createForm = document.getElementById('createChecklistForm');
    if (createForm) {
        // Add a backup submit handler for the create button
        const createBtn = document.getElementById('createBtn');
        if (createBtn) {
            createBtn.addEventListener('click', function(event) {
                console.log('Create button clicked directly');
                
                // Don't submit if form isn't valid
                if (!createForm.checkValidity()) {
                    return;
                }
                
                // Don't prevent default - allow normal form submission
                console.log('Allowing normal form submission');
                
                // Add loading state
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...';
                
                // Don't disable to ensure form submission works
                // this.disabled = true;
            });
        }
    }
});

/* CSS via JS - for the pulse animation */
document.head.insertAdjacentHTML('beforeend', `
<style>
.pulse-animation {
    animation: pulse-effect 0.5s;
}

@keyframes pulse-effect {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.03);
    }
    100% {
        transform: scale(1);
    }
}
</style>
`); 