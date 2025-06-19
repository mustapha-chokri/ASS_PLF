/**
 * Main JavaScript utilities for the application
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ تم تحميل ملف main.js بنجاح!');
    
    // تهيئة حالة القائمة الجانبية
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const sidebarToggle = document.getElementById('sidebarCollapse');
    
    console.log('العناصر الموجودة:', {
        sidebar: !!sidebar,
        content: !!content,
        sidebarToggle: !!sidebarToggle
    });
    
    // القائمة الجانبية مخفية افتراضياً على جميع الأحجام
    if (sidebar) sidebar.classList.add('active');
    if (content) content.classList.add('active');
    
    // Sidebar toggle functionality - إصلاح مشكلة الإظهار/الإخفاء
    if (sidebarToggle) {
        console.log('تم العثور على زر إظهار/إخفاء القائمة');
        
        sidebarToggle.addEventListener('click', function(event) {
            event.stopPropagation(); // منع انتشار الحدث
            event.preventDefault(); // منع السلوك الافتراضي
            
            console.log('تم الضغط على زر إظهار/إخفاء القائمة');
            
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            
            if (sidebar && content) {
                // تبديل حالة القائمة الجانبية
                sidebar.classList.toggle('active');
                content.classList.toggle('active');
                
                console.log('Sidebar toggle clicked');
                console.log('Sidebar active (hidden):', sidebar.classList.contains('active'));
                console.log('Content active (expanded):', content.classList.contains('active'));
            } else {
                console.error('لم يتم العثور على عناصر القائمة الجانبية');
            }
        });
    } else {
        console.error('لم يتم العثور على زر إظهار/إخفاء القائمة');
    }
    
    // إخفاء القائمة الجانبية فقط عند الضغط على الروابط الفعلية (وليس الأقسام الفرعية)
    const sidebarLinks = document.querySelectorAll('#sidebar a[href]:not([data-bs-toggle])');
    sidebarLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            // إخفاء القائمة الجانبية على جميع الأحجام
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            if (sidebar && content) {
                sidebar.classList.add('active');
                content.classList.add('active');
                console.log('Sidebar hidden after clicking actual link');
            }
        });
    });
    
    // إخفاء القائمة الجانبية عند الضغط على أي رابط في القائمة الفرعية
    const submenuLinks = document.querySelectorAll('#sidebar ul ul a');
    submenuLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            if (sidebar && content) {
                sidebar.classList.add('active');
                content.classList.add('active');
                console.log('Submenu link clicked - sidebar hidden');
            }
        });
    });
    
    // إخفاء القائمة الجانبية عند النقر على أي رابط في القائمة (وليس الأقسام الفرعية)
    document.addEventListener('click', function(event) {
        const sidebarToggle = document.getElementById('sidebarCollapse');
        
        // التحقق من أن النقر كان على رابط في القائمة الجانبية وليس على زر الإظهار أو قسم فرعي
        if (event.target.closest('#sidebar a[href]:not([data-bs-toggle])') && !sidebarToggle.contains(event.target)) {
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            if (sidebar && content) {
                sidebar.classList.add('active');
                content.classList.add('active');
                console.log('Sidebar link clicked - hidden');
            }
        }
    });
    
    // إخفاء القائمة الجانبية عند الضغط خارجها (فقط على الشاشات الصغيرة)
    document.addEventListener('click', function(event) {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarCollapse');
        
        if (sidebar && !sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
            // إخفاء القائمة الجانبية على الشاشات الصغيرة فقط
            if (window.innerWidth <= 768) {
                sidebar.classList.add('active');
                document.getElementById('content').classList.add('active');
                console.log('Clicked outside sidebar - hidden (mobile)');
            }
        }
    });
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
    
    // Initialize datepickers on all date input fields
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        if (input.value === '') {
            const today = new Date();
            const year = today.getFullYear();
            let month = today.getMonth() + 1;
            let day = today.getDate();
            
            // Format month and day to have leading zeros if needed
            month = month < 10 ? '0' + month : month;
            day = day < 10 ? '0' + day : day;
            
            input.valueAsDate = today;
        }
    });
    
    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });
    
    // Tooltips initialization for Bootstrap 5
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Replace missing profile images with a fallback
    const images = document.querySelectorAll('img.img-profile');
    
    images.forEach(img => {
        img.addEventListener('error', function() {
            // If image fails to load, replace with a data URI placeholder
            this.src = 'data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%22200%22%20height%3D%22200%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20200%20200%22%20preserveAspectRatio%3D%22none%22%3E%3Cdefs%3E%3Cstyle%20type%3D%22text%2Fcss%22%3E%23holder_1805cf1eec7%20text%20%7B%20fill%3Argba(255%2C255%2C255%2C.75)%3Bfont-weight%3Anormal%3Bfont-family%3AHelvetica%2C%20monospace%3Bfont-size%3A10pt%20%7D%20%3C%2Fstyle%3E%3C%2Fdefs%3E%3Cg%20id%3D%22holder_1805cf1eec7%22%3E%3Crect%20width%3D%22200%22%20height%3D%22200%22%20fill%3D%22%23777%22%3E%3C%2Frect%3E%3Cg%3E%3Ctext%20x%3D%2274.390625%22%20y%3D%22104.5%22%3E%3C%2Ftext%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E';
            this.alt = 'صورة شخصية';
        });
    });
    
    // Fix for custom checkboxes in tables
    const customCheckboxes = document.querySelectorAll('.custom-control-input');
    if (customCheckboxes.length > 0) {
        console.log(`Found ${customCheckboxes.length} custom checkboxes`);
        
        // Ensure custom checkboxes have proper events
        customCheckboxes.forEach(checkbox => {
            // Make sure the checkbox is properly initialized
            checkbox.addEventListener('change', function() {
                console.log(`Checkbox ${this.id} changed to ${this.checked}`);
                
                // Make sure the parent knows about the change
                const event = new Event('change', { bubbles: true });
                this.dispatchEvent(event);
            });
        });
    }
});

// إزالة مراقبة تغيير حجم النافذة تماماً لتجنب الإظهار التلقائي 