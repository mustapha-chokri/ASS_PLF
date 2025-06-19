/**
 * ملف خاص بوظائف صفحة الطلاب
 */
console.log('✅ تم تحميل ملف students.js بنجاح!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف سكريبت صفحة الطلاب');

    // التحقق من وجود جدول البيانات
    const dataTable = document.getElementById('dataTable');
    if (!dataTable) {
        console.warn('لم يتم العثور على جدول البيانات');
        return;
    }

    // تهيئة DataTables مع دعم RTL
    const table = $('#dataTable').DataTable({
        language: {
            url: "//cdn.datatables.net/plug-ins/1.10.25/i18n/Arabic.json"
        },
        order: [[1, "desc"]],
        columnDefs: [
            { orderable: false, targets: 0 }
        ]
    });

    // المتغيرات العامة
    let selectedStudents = [];
    
    // الأزرار وعناصر العرض
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const btnSelectAll = document.getElementById('btnSelectAll');
    const btnDeselectAll = document.getElementById('btnDeselectAll');
    const btnAddToBlacklist = document.getElementById('btnAddToBlacklist');
    const btnDeleteSelected = document.getElementById('btnDeleteSelected');
    const btnWhatsAppSelected = document.getElementById('btnWhatsAppSelected');
    
    // عناصر عرض العدادات
    const blacklistCountSpan = document.getElementById('blacklistCount');
    const deleteCountSpan = document.getElementById('deleteCount');
    const whatsappCountSpan = document.getElementById('whatsappCount');

    // دالة لتحديث عدادات التلاميذ المحددين وحالة الأزرار
    function updateCounters() {
        const count = selectedStudents.length;
        const whatsappCount = selectedStudents.filter(s => s.phone && s.phone.trim() !== '').length;
        
        if (blacklistCountSpan) blacklistCountSpan.textContent = count;
        if (deleteCountSpan) deleteCountSpan.textContent = count;
        if (whatsappCountSpan) whatsappCountSpan.textContent = whatsappCount;
        
        if (btnAddToBlacklist) btnAddToBlacklist.disabled = count === 0;
        if (btnDeleteSelected) btnDeleteSelected.disabled = count === 0;
        if (btnWhatsAppSelected) btnWhatsAppSelected.disabled = whatsappCount === 0;
        
        console.log(`تم تحديث العدادات: ${count} تلميذ محدد، ${whatsappCount} لديهم رقم واتساب`);
    }

    // دالة لتحديث حالة مربع تحديد "تحديد الكل"
    function updateSelectAllCheckbox() {
        if (!selectAllCheckbox) return;
        
        const checkboxes = document.querySelectorAll('.studentCheckbox');
        const checkboxCount = checkboxes.length;
        const checkedCount = document.querySelectorAll('.studentCheckbox:checked').length;
        
        selectAllCheckbox.checked = checkboxCount > 0 && checkboxCount === checkedCount;
        selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < checkboxCount;
    }

    // معالجة حدث تغيير مربع تحديد "تحديد الكل"
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            console.log(`حدث تغيير في مربع "تحديد الكل": ${isChecked}`);
            
            document.querySelectorAll('.studentCheckbox').forEach(checkbox => {
                checkbox.checked = isChecked;
                
                const id = parseInt(checkbox.dataset.id);
                const name = checkbox.dataset.name;
                const phone = checkbox.dataset.phone;
                
                if (isChecked && !selectedStudents.some(s => s.id === id)) {
                    selectedStudents.push({ id, name, phone });
                } else if (!isChecked) {
                    selectedStudents = selectedStudents.filter(s => s.id !== id);
                }
            });
            
            updateCounters();
        });
    }

    // معالجة تغيير مربعات التحديد الفردية عبر تفويض الأحداث
    dataTable.addEventListener('change', function(e) {
        if (e.target.classList.contains('studentCheckbox') || e.target.classList.contains('form-check-input')) {
            const checkbox = e.target;
            const id = parseInt(checkbox.dataset.id);
            const name = checkbox.dataset.name;
            const phone = checkbox.dataset.phone;
            
            console.log(`تم تغيير حالة مربع التحديد للتلميذ ${name}: ${checkbox.checked}`);
            
            if (checkbox.checked) {
                if (!selectedStudents.some(s => s.id === id)) {
                    selectedStudents.push({ id, name, phone });
                }
            } else {
                selectedStudents = selectedStudents.filter(s => s.id !== id);
            }
            
            updateSelectAllCheckbox();
            updateCounters();
        }
    });

    // زر "تحديد الكل"
    if (btnSelectAll) {
        btnSelectAll.addEventListener('click', function() {
            console.log('تم الضغط على زر "تحديد الكل"');
            
            document.querySelectorAll('.studentCheckbox').forEach(checkbox => {
                checkbox.checked = true;
                
                const id = parseInt(checkbox.dataset.id);
                const name = checkbox.dataset.name;
                const phone = checkbox.dataset.phone;
                
                if (!selectedStudents.some(s => s.id === id)) {
                    selectedStudents.push({ id, name, phone });
                }
            });
            
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = true;
                selectAllCheckbox.indeterminate = false;
            }
            
            updateCounters();
        });
    }

    // زر "إلغاء تحديد الكل"
    if (btnDeselectAll) {
        btnDeselectAll.addEventListener('click', function() {
            console.log('تم الضغط على زر "إلغاء تحديد الكل"');
            
            document.querySelectorAll('.studentCheckbox').forEach(checkbox => {
                checkbox.checked = false;
            });
            
            selectedStudents = [];
            
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            }
            
            updateCounters();
        });
    }

    // زر "إضافة المحددين للقائمة السوداء"
    if (btnAddToBlacklist) {
        btnAddToBlacklist.addEventListener('click', function() {
            if (selectedStudents.length === 0) return;
            
            console.log('تم الضغط على زر "إضافة المحددين للقائمة السوداء"');
            
            const blacklistStudentsList = document.getElementById('blacklistStudentsList');
            if (blacklistStudentsList) {
                blacklistStudentsList.innerHTML = '';
                
                selectedStudents.forEach(student => {
                    const li = document.createElement('li');
                    li.textContent = student.name;
                    blacklistStudentsList.appendChild(li);
                });
            }
            
            const blacklistStudentIds = document.getElementById('blacklistStudentIds');
            if (blacklistStudentIds) {
                blacklistStudentIds.value = selectedStudents.map(s => s.id).join(',');
            }
            
            // عرض النافذة المنبثقة
            try {
                const bulkBlacklistModal = new bootstrap.Modal(document.getElementById('bulkBlacklistModal'));
                bulkBlacklistModal.show();
                console.log('تم عرض نافذة القائمة السوداء بنجاح');
            } catch (error) {
                console.error('خطأ عند محاولة عرض نافذة القائمة السوداء:', error);
                alert('حدث خطأ في عرض نافذة القائمة السوداء');
            }
        });
    }

    // زر "حذف المحددين"
    if (btnDeleteSelected) {
        btnDeleteSelected.addEventListener('click', function() {
            if (selectedStudents.length === 0) return;
            
            console.log('تم الضغط على زر "حذف المحددين"');
            
            const deleteStudentsList = document.getElementById('deleteStudentsList');
            if (deleteStudentsList) {
                deleteStudentsList.innerHTML = '';
                
                selectedStudents.forEach(student => {
                    const li = document.createElement('li');
                    li.textContent = student.name;
                    deleteStudentsList.appendChild(li);
                });
            }
            
            const deleteStudentIds = document.getElementById('deleteStudentIds');
            if (deleteStudentIds) {
                deleteStudentIds.value = selectedStudents.map(s => s.id).join(',');
            }
            
            // عرض النافذة المنبثقة
            try {
                const bulkDeleteModal = new bootstrap.Modal(document.getElementById('bulkDeleteModal'));
                bulkDeleteModal.show();
                console.log('تم عرض نافذة الحذف بنجاح');
            } catch (error) {
                console.error('خطأ عند محاولة عرض نافذة الحذف:', error);
                alert('حدث خطأ في عرض نافذة الحذف');
            }
        });
    }

    // زر "إرسال رسالة واتساب للمحددين"
    if (btnWhatsAppSelected) {
        btnWhatsAppSelected.addEventListener('click', function() {
            const studentsWithPhone = selectedStudents.filter(s => s.phone && s.phone.trim() !== '');
            
            if (studentsWithPhone.length === 0) {
                alert('لا يوجد أي تلميذ من المحددين لديه رقم هاتف!');
                return;
            }
            
            console.log('تم الضغط على زر "إرسال رسالة واتساب للمحددين"');
            
            const whatsappStudentsList = document.getElementById('whatsappStudentsList');
            if (whatsappStudentsList) {
                whatsappStudentsList.innerHTML = '';
                
                studentsWithPhone.forEach(student => {
                    const li = document.createElement('li');
                    li.textContent = `${student.name} (${student.phone})`;
                    whatsappStudentsList.appendChild(li);
                });
            }
            
            // عرض النافذة المنبثقة
            try {
                const whatsappModal = new bootstrap.Modal(document.getElementById('whatsappModal'));
                whatsappModal.show();
                console.log('تم عرض نافذة الواتساب بنجاح');
            } catch (error) {
                console.error('خطأ عند محاولة عرض نافذة الواتساب:', error);
                alert('حدث خطأ في عرض نافذة الواتساب');
            }
        });
    }

    // زر "إرسال" في نافذة الواتساب
    const btnSendWhatsApp = document.getElementById('btnSendWhatsApp');
    if (btnSendWhatsApp) {
        btnSendWhatsApp.addEventListener('click', function() {
            const message = document.getElementById('whatsapp_message').value;
            
            if (!message) {
                alert('الرجاء كتابة نص الرسالة!');
                return;
            }
            
            console.log('جاري إرسال رسائل الواتساب');
            
            const studentsWithPhone = selectedStudents.filter(s => s.phone && s.phone.trim() !== '');
            
            studentsWithPhone.forEach(student => {
                const personalizedMessage = message.replace('[اسم_التلميذ]', student.name);
                const encodedMessage = encodeURIComponent(personalizedMessage);
                const phone = student.phone.replace('+', '').replace(/\s/g, '');
                const url = `https://wa.me/${phone}?text=${encodedMessage}`;
                window.open(url, '_blank');
            });
            
            // إغلاق النافذة المنبثقة
            try {
                const whatsappModal = bootstrap.Modal.getInstance(document.getElementById('whatsappModal'));
                if (whatsappModal) {
                    whatsappModal.hide();
                }
                console.log('تم إغلاق نافذة الواتساب بنجاح');
            } catch (error) {
                console.error('خطأ عند محاولة إغلاق نافذة الواتساب:', error);
            }
        });
    }

    // التحقق من استمارة إضافة القائمة السوداء
    const bulkBlacklistForm = document.getElementById('bulkBlacklistForm');
    if (bulkBlacklistForm) {
        bulkBlacklistForm.addEventListener('submit', function(e) {
            const reason = document.getElementById('bulk_blacklist_reason').value;
            if (!reason) {
                e.preventDefault();
                alert('الرجاء كتابة سبب الإضافة إلى القائمة السوداء');
                return false;
            }
        });
    }

    // التحقق من استمارة الحذف الجماعي
    const bulkDeleteForm = document.getElementById('bulkDeleteForm');
    if (bulkDeleteForm) {
        bulkDeleteForm.addEventListener('submit', function(e) {
            if (!confirm('هل أنت متأكد من حذف التلاميذ المحددين؟ لا يمكن التراجع عن هذا الإجراء.')) {
                e.preventDefault();
                return false;
            }
        });
    }

    // تهيئة العدادات عند تحميل الصفحة
    updateCounters();

    // مساعدة في تصحيح الأخطاء - تحقق من الأزرار والمكونات
    console.log({
        dataTable: !!dataTable,
        selectAllCheckbox: !!selectAllCheckbox,
        btnSelectAll: !!btnSelectAll,
        btnDeselectAll: !!btnDeselectAll,
        btnAddToBlacklist: !!btnAddToBlacklist,
        btnDeleteSelected: !!btnDeleteSelected,
        btnWhatsAppSelected: !!btnWhatsAppSelected
    });

    // --- إصلاح مشكلة إعادة رسم الجدول وفقدان التحديد ---
    function restoreCheckboxStates() {
        // إعادة تفعيل مربعات التحديد حسب selectedStudents
        document.querySelectorAll('.studentCheckbox').forEach(checkbox => {
            const id = parseInt(checkbox.dataset.id);
            checkbox.checked = selectedStudents.some(s => s.id === id);
        });
        updateSelectAllCheckbox();
        updateCounters();
    }

    // إعادة ربط الأحداث بعد كل عملية رسم للجدول
    if (table) {
        table.on('draw', function() {
            restoreCheckboxStates();
        });
    }

    // --- اختبار عمل الأزرار الجماعية ---
    [btnAddToBlacklist, btnDeleteSelected, btnWhatsAppSelected, btnSelectAll, btnDeselectAll].forEach(function(btn) {
        if (btn) {
            btn.addEventListener('click', function() {
                console.log('تم الضغط على زر جماعي:', this.id);
            });
        }
    });
}); 