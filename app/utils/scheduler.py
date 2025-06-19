from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
from app.controllers.vehicles.routes import check_vehicle_licenses

# إنشاء متغير عام للمجدول
scheduler = None

def init_scheduler(app):
    """تهيئة المجدول"""
    global scheduler
    
    if scheduler is None:
        scheduler = BackgroundScheduler()
        
        # جدولة فحص الرخص يومياً في الساعة 8 صباحاً
        scheduler.add_job(
            func=check_vehicle_licenses,
            trigger=CronTrigger(hour=8, minute=0),
            id='check_licenses',
            name='فحص تواريخ انتهاء الرخص',
            replace_existing=True
        )
        
        # بدء المجدول
        scheduler.start()
        
        # إيقاف المجدول عند إغلاق التطبيق
        @app.teardown_appcontext
        def shutdown_scheduler(exception=None):
            global scheduler
            if scheduler and scheduler.running:
                scheduler.shutdown()
                scheduler = None 