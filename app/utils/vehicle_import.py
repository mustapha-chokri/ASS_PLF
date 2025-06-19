import pandas as pd
from app.models.vehicle import Vehicle
from app import db

def import_vehicles_from_excel(file):
    """استيراد بيانات المركبات من ملف إكسل"""
    try:
        # قراءة ملف الإكسل
        df = pd.read_excel(file)
        
        # طباعة أسماء الأعمدة الموجودة للمساعدة في التشخيص
        print("الأعمدة الموجودة في الملف:", df.columns.tolist())
        
        # التحقق من وجود الأعمدة المطلوبة
        required_columns = ['رقم التسجيل', 'نوع المركبة', 'الموديل', 'سنة الصنع']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"الأعمدة المطلوبة غير موجودة: {', '.join(missing_columns)}"
            print(error_msg)
            raise ValueError(error_msg)
        
        # تحويل التواريخ
        date_columns = ['تاريخ الشراء', 'تاريخ انتهاء التسجيل', 'تاريخ انتهاء التأمين', 
                      'تاريخ انتهاء الفحص', 'تاريخ انتهاء رخصة القيادة']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # إضافة أو تحديث المركبات
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # التحقق من وجود رقم التسجيل
                if pd.isna(row['رقم التسجيل']):
                    raise ValueError("رقم التسجيل مطلوب")
                
                # التحقق من وجود نوع المركبة
                if pd.isna(row['نوع المركبة']):
                    raise ValueError("نوع المركبة مطلوب")
                
                # التحقق من وجود الموديل
                if pd.isna(row['الموديل']):
                    raise ValueError("الموديل مطلوب")
                
                # التحقق من وجود سنة الصنع
                if pd.isna(row['سنة الصنع']):
                    raise ValueError("سنة الصنع مطلوبة")
                
                vehicle = Vehicle.query.filter_by(registration_number=row['رقم التسجيل']).first()
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
                print(f"خطأ في السطر {index + 2}: {str(e)}")
                continue
        
        if error_count > 0:
            print(f"تم استيراد {success_count} سجل بنجاح")
            print(f"فشل استيراد {error_count} سجل")
            print("تفاصيل الأخطاء:", "\n".join(errors))
            raise ValueError(f"تم استيراد {success_count} سجل بنجاح، وفشل استيراد {error_count} سجل")
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"حدث خطأ أثناء استيراد البيانات: {str(e)}"
        print(error_msg)
        raise ValueError(error_msg) 