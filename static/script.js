// KinderSlides JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('topicForm');
    const generateBtn = document.getElementById('generateBtn');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    const topicSelect = document.getElementById('topic');
    
    // Topic descriptions for enhanced user experience
    const topicDescriptions = {
        'ABC': {
            description: '26 beautiful slides covering A-Z with fun illustrations!',
            icon: 'fas fa-font',
            color: 'text-primary'
        },
        'Numbers 1-5': {
            description: '5 colorful slides to help kids learn counting!',
            icon: 'fas fa-calculator', 
            color: 'text-success'
        },
        'Shapes': {
            description: '6 slides featuring basic shapes with fun examples!',
            icon: 'fas fa-shapes',
            color: 'text-warning'
        },
        'Colors': {
            description: '8 vibrant slides teaching primary and secondary colors!',
            icon: 'fas fa-palette',
            color: 'text-info'
        }
    };
    
    // Add visual feedback when topic is selected
    topicSelect.addEventListener('change', function() {
        const selectedTopic = this.value;
        updateGenerateButton(selectedTopic);
        addTopicFeedback(selectedTopic);
    });
    
    function updateGenerateButton(topic) {
        if (topic) {
            generateBtn.classList.add('pulse-animation');
            generateBtn.innerHTML = `<i class="fas fa-cogs me-2"></i>Generate ${topic} Presentation`;
        } else {
            generateBtn.classList.remove('pulse-animation');
            generateBtn.innerHTML = '<i class="fas fa-cogs me-2"></i>Generate Presentation';
        }
    }
    
    function addTopicFeedback(topic) {
        // Remove existing feedback
        const existingFeedback = document.querySelector('.topic-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        if (topic && topicDescriptions[topic]) {
            const info = topicDescriptions[topic];
            const feedback = document.createElement('div');
            feedback.className = 'topic-feedback alert alert-info mt-3';
            feedback.innerHTML = `
                <i class="${info.icon} ${info.color} me-2"></i>
                ${info.description}
            `;
            
            topicSelect.parentNode.appendChild(feedback);
            
            // Add animation
            feedback.style.opacity = '0';
            feedback.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                feedback.style.transition = 'all 0.3s ease';
                feedback.style.opacity = '1';
                feedback.style.transform = 'translateY(0)';
            }, 100);
        }
    }
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        const selectedTopic = topicSelect.value;
        
        if (!selectedTopic) {
            e.preventDefault();
            showAlert('Please select a topic before generating!', 'warning');
            return;
        }
        
        // Show loading modal
        loadingModal.show();
        
        // Disable the form to prevent double submission
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating Presentation...';
        
        // Add a timeout to hide modal in case of errors
        setTimeout(() => {
            if (loadingModal._isShown) {
                loadingModal.hide();
                generateBtn.disabled = false;
                updateGenerateButton(selectedTopic);
                showAlert('Generation is taking longer than expected. Please check if the download started.', 'info');
            }
        }, 30000); // 30 seconds timeout
    });
    
    // Handle successful download (when modal needs to be hidden)
    window.addEventListener('focus', function() {
        setTimeout(() => {
            if (loadingModal._isShown) {
                loadingModal.hide();
                generateBtn.disabled = false;
                const selectedTopic = topicSelect.value;
                updateGenerateButton(selectedTopic);
                showAlert('Presentation generated successfully! Check your downloads folder.', 'success');
            }
        }, 2000);
    });
    
    function showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.dynamic-alert');
        existingAlerts.forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show dynamic-alert`;
        alertDiv.innerHTML = `
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert after the header
        const header = document.querySelector('.kindergarten-title').parentNode;
        header.insertAdjacentElement('afterend', alertDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv && alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    function getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'danger': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    // Add pulse animation to button
    const style = document.createElement('style');
    style.textContent = `
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .topic-feedback {
            border-radius: 15px;
            border: 2px solid var(--kindergarten-info);
            background-color: rgba(78, 205, 196, 0.1);
        }
    `;
    document.head.appendChild(style);
    
    // Add hover effects to preview cards
    const previewCards = document.querySelectorAll('.kindergarten-preview');
    previewCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Add click-to-select functionality for preview cards
    previewCards.forEach((card, index) => {
        card.addEventListener('click', function() {
            const topics = ['ABC', 'Numbers 1-5', 'Shapes', 'Colors'];
            const topic = topics[index];
            if (topic) {
                topicSelect.value = topic;
                topicSelect.dispatchEvent(new Event('change'));
                
                // Scroll to form
                document.getElementById('topicForm').scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
                
                // Add visual feedback
                card.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    card.style.transform = 'translateY(-5px) scale(1.02)';
                }, 150);
            }
        });
        
        // Add cursor pointer to indicate clickability
        card.style.cursor = 'pointer';
    });
    
    // Accessibility improvements
    topicSelect.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (this.value) {
                form.dispatchEvent(new Event('submit'));
            }
        }
    });
    
    // Add smooth scrolling for better UX
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
