from app import db
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import send_file

class VehicleType(db.Model):
    """أنواع السيارات"""
    __tablename__ = 'vehicle_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<VehicleType {self.name}>'

class VehicleStatus(db.Model):
    """حالات السيارات"""
    __tablename__ = 'vehicle_statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<VehicleStatus {self.name}>'

class Vehicle(db.Model):
    """نموذج السيارات"""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    capacity = db.Column(db.Integer)
    status = db.Column(db.String(20), default='active')
    purchase_price = db.Column(db.Float)
    purchase_date = db.Column(db.Date)
    registration_expiry = db.Column(db.Date)
    insurance_expiry = db.Column(db.Date)
    inspection_expiry = db.Column(db.Date)
    driving_license_expiry = db.Column(db.Date)
    current_mileage = db.Column(db.Integer)
    next_maintenance_mileage = db.Column(db.Integer)
    next_maintenance_type = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    maintenances = db.relationship('VehicleMaintenance', back_populates='vehicle', lazy=True)
    assignments = db.relationship('DriverVehicleAssignment', back_populates='vehicle', lazy=True)

    def __repr__(self):
        return f'<Vehicle {self.registration_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'registration_number': self.registration_number,
            'vehicle_type': self.vehicle_type,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'capacity': self.capacity,
            'status': self.status,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'registration_expiry': self.registration_expiry.isoformat() if self.registration_expiry else None,
            'insurance_expiry': self.insurance_expiry.isoformat() if self.insurance_expiry else None,
            'inspection_expiry': self.inspection_expiry.isoformat() if self.inspection_expiry else None,
            'driving_license_expiry': self.driving_license_expiry.isoformat() if self.driving_license_expiry else None,
            'current_mileage': self.current_mileage,
            'next_maintenance_mileage': self.next_maintenance_mileage,
            'next_maintenance_type': self.next_maintenance_type,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
    @classmethod
    def export_to_excel(cls):
        """تصدير بيانات المركبات إلى ملف إكسل"""
        try:
            # جلب جميع المركبات
            vehicles = cls.query.all()
            
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
    
    @classmethod
    def import_from_excel(cls, file):
        """استيراد بيانات المركبات من ملف إكسل"""
        try:
            # قراءة ملف الإكسل
            df = pd.read_excel(file)
            
            # التحقق من وجود الأعمدة المطلوبة
            required_columns = ['رقم التسجيل', 'نوع المركبة', 'الموديل', 'سنة الصنع']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"الأعمدة المطلوبة غير موجودة: {', '.join(missing_columns)}")
            
            # تحويل التواريخ
            date_columns = ['تاريخ الشراء', 'تاريخ انتهاء التسجيل', 'تاريخ انتهاء التأمين', 
                          'تاريخ انتهاء الفحص', 'تاريخ انتهاء رخصة القيادة']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # إضافة أو تحديث المركبات
            for _, row in df.iterrows():
                vehicle = cls.query.filter_by(registration_number=row['رقم التسجيل']).first()
                if not vehicle:
                    vehicle = cls()
                
                # تحديث البيانات
                vehicle.registration_number = row['رقم التسجيل']
                vehicle.vehicle_type = row['نوع المركبة']
                vehicle.brand = row.get('العلامة التجارية')
                vehicle.model = row['الموديل']
                vehicle.year = str(row['سنة الصنع'])
                vehicle.capacity = row.get('السعة')
                vehicle.status = row.get('الحالة', 'active')
                vehicle.purchase_price = row.get('سعر الشراء')
                vehicle.purchase_date = row.get('تاريخ الشراء')
                vehicle.registration_expiry = row.get('تاريخ انتهاء التسجيل')
                vehicle.insurance_expiry = row.get('تاريخ انتهاء التأمين')
                vehicle.inspection_expiry = row.get('تاريخ انتهاء الفحص')
                vehicle.driving_license_expiry = row.get('تاريخ انتهاء رخصة القيادة')
                vehicle.current_mileage = row.get('المسافة المقطوعة')
                vehicle.next_maintenance_mileage = row.get('المسافة للصيانة القادمة')
                vehicle.next_maintenance_type = row.get('نوع الصيانة القادمة')
                vehicle.notes = row.get('ملاحظات')
                
                db.session.add(vehicle)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error importing vehicles from Excel: {str(e)}")
            return False

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    license_number = db.Column(db.String(20), unique=True, nullable=False)
    license_expiry = db.Column(db.Date, nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    hire_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive, suspended
    photo_path = db.Column(db.String(256), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle_assignments = db.relationship('DriverVehicleAssignment', back_populates='driver', lazy='dynamic')
    
    def __repr__(self):
        return f'<Driver {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

class DriverVehicleAssignment(db.Model):
    __tablename__ = 'driver_vehicle_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    driver = db.relationship('Driver', back_populates='vehicle_assignments')
    vehicle = db.relationship('Vehicle', back_populates='assignments')

    __table_args__ = (
        db.UniqueConstraint('driver_id', 'vehicle_id', name='uq_driver_vehicle_assignment'),
    )

    def __repr__(self):
        return f'<DriverVehicleAssignment {self.id}>'

class VehicleMaintenance(db.Model):
    __tablename__ = 'vehicle_maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # نوع الصيانة
    status = db.Column(db.String(20), default='scheduled')  # حالة الصيانة
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    cost = db.Column(db.Float)
    description = db.Column(db.Text)
    service_provider = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    maintenance_date = db.Column(db.Date)  # تاريخ الصيانة
    current_mileage = db.Column(db.Integer)  # الكيلومتراج الحالي
    next_maintenance_mileage = db.Column(db.Integer)  # الكيلومتراج الذي ستم فيه الصيانة القادمة

    # العلاقات
    vehicle = db.relationship('Vehicle', back_populates='maintenances')
    creator = db.relationship('User', backref='maintenance_records')

    def __repr__(self):
        return f'<VehicleMaintenance {self.id}>' 