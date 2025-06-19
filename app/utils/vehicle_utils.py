import pandas as pd
from io import BytesIO
from app.models.vehicle import Vehicle
from app import db
from datetime import datetime

def export_vehicles_to_excel():
    """تصدير بيانات المركبات إلى ملف إكسل"""
    try:
        # جلب جميع المركبات
        vehicles = Vehicle.query.all()
        
        # تحويل البيانات إلى DataFrame
        data = []
        for vehicle in vehicles:
            data.append({
                'رقم التسجيل': vehicle.registration_number,
                'نوع المركبة': vehicle.vehicle_type,
                'العلامة التجارية': vehicle.brand,
                'الموديل': vehicle.model,
                'سنة الصنع': vehicle.year,
                'السعة': vehicle.capacity,
                'الحالة': vehicle.status,
                'سعر الشراء': vehicle.purchase_price,
                'تاريخ الشراء': vehicle.purchase_date,
                'تاريخ انتهاء التسجيل': vehicle.registration_expiry,
                'تاريخ انتهاء التأمين': vehicle.insurance_expiry,
                'تاريخ انتهاء الفحص': vehicle.inspection_expiry,
                'تاريخ انتهاء رخصة القيادة': vehicle.driving_license_expiry,
                'المسافة المقطوعة': vehicle.current_mileage,
                'المسافة للصيانة القادمة': vehicle.next_maintenance_mileage,
                'نوع الصيانة القادمة': vehicle.next_maintenance_type,
                'ملاحظات': vehicle.notes
            })
        
        df = pd.DataFrame(data)
        
        # إنشاء ملف إكسل في الذاكرة
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='المركبات', index=False)
            
            # تنسيق الأعمدة
            worksheet = writer.sheets['المركبات']
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_width)
        
        output.seek(0)
        return output
        
    except Exception as e:
        print(f"Error exporting vehicles to Excel: {str(e)}")
        return None

def import_vehicles_from_excel(file):
    """استيراد بيانات السيارات من ملف إكسل"""
    try:
        # قراءة ملف الإكسل
        df = pd.read_excel(file)
        
        # التحقق من وجود الأعمدة المطلوبة
        required_columns = ['رقم التسجيل', 'نوع المركبة', 'الموديل', 'سنة الصنع']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"الأعمدة المطلوبة غير موجودة: {', '.join(missing_columns)}"
        
        # تحويل التواريخ
        date_columns = ['تاريخ الشراء', 'تاريخ انتهاء التسجيل', 'تاريخ انتهاء التأمين', 
                      'تاريخ انتهاء الفحص', 'تاريخ انتهاء رخصة القيادة']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # إضافة أو تحديث السيارات
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # التحقق من البيانات الإلزامية
                if pd.isna(row['رقم التسجيل']):
                    raise ValueError("رقم التسجيل مطلوب")
                if pd.isna(row['نوع المركبة']):
                    raise ValueError("نوع المركبة مطلوب")
                if pd.isna(row['الموديل']):
                    raise ValueError("الموديل مطلوب")
                if pd.isna(row['سنة الصنع']):
                    raise ValueError("سنة الصنع مطلوبة")
                
                # البحث عن السيارة أو إنشاء سيارة جديدة
                vehicle = Vehicle.query.filter_by(registration_number=str(row['رقم التسجيل']).strip()).first()
                if not vehicle:
                    vehicle = Vehicle()
                
                # تحديث البيانات
                vehicle.registration_number = str(row['رقم التسجيل']).strip()
                vehicle.vehicle_type = str(row['نوع المركبة']).strip()
                vehicle.brand = str(row.get('العلامة التجارية', '')).strip() if not pd.isna(row.get('العلامة التجارية')) else None
                vehicle.model = str(row['الموديل']).strip()
                vehicle.year = str(row['سنة الصنع']).strip()
                vehicle.capacity = int(row['السعة']) if not pd.isna(row.get('السعة')) else None
                vehicle.status = str(row.get('الحالة', 'active')).strip()
                vehicle.purchase_price = float(row['سعر الشراء']) if not pd.isna(row.get('سعر الشراء')) else None
                vehicle.purchase_date = row.get('تاريخ الشراء')
                vehicle.registration_expiry = row.get('تاريخ انتهاء التسجيل')
                vehicle.insurance_expiry = row.get('تاريخ انتهاء التأمين')
                vehicle.inspection_expiry = row.get('تاريخ انتهاء الفحص')
                vehicle.driving_license_expiry = row.get('تاريخ انتهاء رخصة القيادة')
                vehicle.current_mileage = int(row['المسافة المقطوعة']) if not pd.isna(row.get('المسافة المقطوعة')) else None
                vehicle.next_maintenance_mileage = int(row['المسافة للصيانة القادمة']) if not pd.isna(row.get('المسافة للصيانة القادمة')) else None
                vehicle.next_maintenance_type = str(row.get('نوع الصيانة القادمة', '')).strip() if not pd.isna(row.get('نوع الصيانة القادمة')) else None
                vehicle.notes = str(row.get('ملاحظات', '')).strip() if not pd.isna(row.get('ملاحظات')) else None
                
                db.session.add(vehicle)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"خطأ في السطر {index + 2}: {str(e)}")
                continue
        
        if error_count > 0:
            db.session.rollback()
            return False, f"تم استيراد {success_count} سجل بنجاح، وفشل استيراد {error_count} سجل. الأخطاء: {'; '.join(errors)}"
        
        db.session.commit()
        return True, f"تم استيراد {success_count} سجل بنجاح"
        
    except Exception as e:
        db.session.rollback()
        return False, f"حدث خطأ أثناء استيراد البيانات: {str(e)}"

def export_vehicles_template():
    """تصدير نموذج ملف إكسل فارغ"""
    # إنشاء DataFrame فارغ مع الأعمدة المطلوبة
    columns = [
        'رقم التسجيل', 'نوع المركبة', 'العلامة التجارية', 'الموديل', 'سنة الصنع',
        'السعة', 'الحالة', 'سعر الشراء', 'تاريخ الشراء', 'تاريخ انتهاء التسجيل',
        'تاريخ انتهاء التأمين', 'تاريخ انتهاء الفحص', 'تاريخ انتهاء رخصة القيادة',
        'المسافة المقطوعة', 'المسافة للصيانة القادمة', 'نوع الصيانة القادمة', 'ملاحظات'
    ]
    df = pd.DataFrame(columns=columns)
    
    # إضافة صف واحد كمثال
    example_row = {
        'رقم التسجيل': '12345',
        'نوع المركبة': 'سيارة',
        'العلامة التجارية': 'تويوتا',
        'الموديل': 'كامري',
        'سنة الصنع': '2023',
        'السعة': 5,
        'الحالة': 'active',
        'سعر الشراء': 100000,
        'تاريخ الشراء': datetime.now().date(),
        'تاريخ انتهاء التسجيل': datetime.now().date(),
        'تاريخ انتهاء التأمين': datetime.now().date(),
        'تاريخ انتهاء الفحص': datetime.now().date(),
        'تاريخ انتهاء رخصة القيادة': datetime.now().date(),
        'المسافة المقطوعة': 0,
        'المسافة للصيانة القادمة': 5000,
        'نوع الصيانة القادمة': 'صيانة دورية',
        'ملاحظات': 'ملاحظات تجريبية'
    }
    df = pd.concat([df, pd.DataFrame([example_row])], ignore_index=True)
    
    return df 