// Main JavaScript for Gym Website

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initMobileMenu();
    initBookingSystem();
    initCounters();
    initFormValidation();
    initNotifications();
});

// Mobile Menu Toggle
function initMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('show');
        });
    }
}

// Booking System
function initBookingSystem() {
    const bookingForms = document.querySelectorAll('.booking-form');
    
    bookingForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const scheduleId = form.dataset.scheduleId;
            const classDate = form.querySelector('.class-date').value;
            
            // Check availability before booking
            try {
                const response = await fetch(`/api/check-availability/${scheduleId}`);
                const data = await response.json();
                
                if (data.available) {
                    // Submit booking
                    const bookingResponse = await fetch(`/book-class/${scheduleId}`, {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (bookingResponse.ok) {
                        showNotification('Class booked successfully!', 'success');
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    }
                } else {
                    showNotification('Sorry, this class is full.', 'error');
                }
            } catch (error) {
                showNotification('Error booking class. Please try again.', 'error');
                console.error('Booking error:', error);
            }
        });
    });
}

// Animated Counters
function initCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    const animateCounter = (counter) => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const step = target / (duration / 16); // 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += step;
            if (current < target) {
                counter.innerText = Math.round(current).toLocaleString();
                requestAnimationFrame(updateCounter);
            } else {
                counter.innerText = target.toLocaleString();
            }
        };
        
        updateCounter();
    };
    
    // Intersection Observer to trigger counters when visible
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

// Form Validation
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // Password strength meter
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const strength = checkPasswordStrength(this.value);
            updatePasswordStrengthMeter(strength);
        });
    }
}

function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[$@#&!]+/)) strength++;
    
    return strength;
}

function updatePasswordStrengthMeter(strength) {
    const meter = document.getElementById('password-strength');
    if (!meter) return;
    
    const messages = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#20c997'];
    
    meter.innerText = messages[strength - 1] || 'Very Weak';
    meter.style.color = colors[strength - 1] || colors[0];
}

// Notifications System
function initNotifications() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.innerText = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transition = 'opacity 0.5s';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Class Filtering
function initClassFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const classCards = document.querySelectorAll('.class-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.dataset.filter;
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter classes
            classCards.forEach(card => {
                if (filter === 'all' || card.dataset.category === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

// Booking Calendar
function initBookingCalendar() {
    const calendar = document.getElementById('booking-calendar');
    if (!calendar) return;
    
    // Fetch class schedules
    fetch('/api/class-schedules')
        .then(response => response.json())
        .then(schedules => {
            // Render calendar with schedules
            renderCalendar(schedules);
        });
}

function renderCalendar(schedules) {
    // Simple calendar implementation
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    // Get days in month
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    // Create calendar grid
    const calendarGrid = document.getElementById('calendar-grid');
    if (!calendarGrid) return;
    
    calendarGrid.innerHTML = '';
    
    for (let i = 1; i <= daysInMonth; i++) {
        const date = new Date(currentYear, currentMonth, i);
        const dayCell = document.createElement('div');
        dayCell.className = 'calendar-day';
        dayCell.innerHTML = `<span class="date">${i}</span>`;
        
        // Check if there are classes on this day
        const daySchedules = schedules.filter(s => 
            new Date(s.class_date).getDate() === i
        );
        
        if (daySchedules.length > 0) {
            dayCell.classList.add('has-classes');
            dayCell.innerHTML += `<span class="class-count">${daySchedules.length} classes</span>`;
        }
        
        calendarGrid.appendChild(dayCell);
    }
}

// Profile Image Upload Preview
function initImageUpload() {
    const imageInput = document.getElementById('profile-image');
    const imagePreview = document.getElementById('image-preview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

// Membership Calculator
function initMembershipCalculator() {
    const calculator = document.getElementById('membership-calculator');
    if (!calculator) return;
    
    const membershipSelect = calculator.querySelector('#membership-type');
    const durationSelect = calculator.querySelector('#duration');
    const totalDisplay = calculator.querySelector('#total-price');
    
    function calculatePrice() {
        const membershipPrice = parseFloat(membershipSelect.selectedOptions[0].dataset.price);
        const duration = parseInt(durationSelect.value);
        const discount = duration >= 12 ? 0.2 : duration >= 6 ? 0.1 : 0;
        
        const total = membershipPrice * duration * (1 - discount);
        totalDisplay.innerText = `$${total.toFixed(2)}`;
    }
    
    membershipSelect.addEventListener('change', calculatePrice);
    durationSelect.addEventListener('change', calculatePrice);
}

// Social Share
function initSocialShare() {
    const shareButtons = document.querySelectorAll('.share-btn');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const platform = this.dataset.platform;
            const url = encodeURIComponent(window.location.href);
            const title = encodeURIComponent(document.title);
            
            let shareUrl = '';
            
            switch(platform) {
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
                    break;
                case 'linkedin':
                    shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
                    break;
                case 'whatsapp':
                    shareUrl = `https://wa.me/?text=${title}%20${url}`;
                    break;
            }
            
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initClassFilters();
    initBookingCalendar();
    initImageUpload();
    initMembershipCalculator();
    initSocialShare();
});