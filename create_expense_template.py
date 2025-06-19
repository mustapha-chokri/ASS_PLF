import pandas as pd
import os
import xlsxwriter
from pathlib import Path

def create_expense_template():
    data = {
        'العملية': ['شراء لوازم مكتبية', 'فواتير كهرباء'],
        'المبلغ': [150.50, 300.00],
        'التاريخ': ['YYYY-MM-DD', 'YYYY-MM-DD'],
        'نوع المصروف': ['لوازم مكتبية', 'فواتير وخدمات'],
        'المسؤول': ['اسم المستخدم الكامل', 'اسم المستخدم الكامل'],
        'رقم الفاتورة': ['INV-001', ''], # اختياري
        'ملاحظات': ['شراء أقلام ودفاتر', ''] # اختياري
    }
    df = pd.DataFrame(data)

    # الحصول على المسار الحالي للسكريبت
    current_script_path = Path(__file__).resolve()
    # البحث عن مجلد ASS_PLF في المسار
    project_root = current_script_path
    while project_root.name != "ASS_PLF":
        project_root = project_root.parent

    # إنشاء مجلد القوالب إذا لم يكن موجوداً
    template_dir = project_root / 'app' / 'static' / 'templates'
    template_dir.mkdir(parents=True, exist_ok=True)
    template_path = template_dir / 'expense_template.xlsx'

    # إضافة طباعة لمسار الحفظ للتأكد
    print(f"سيتم حفظ قالب المصاريف في: {template_path}")

    # حفظ الملف
    with pd.ExcelWriter(template_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='المصاريف', index=False)
        
        # الحصول على ورقة العمل
        worksheet = writer.sheets['المصاريف']
        
        # تنسيق الأعمدة
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            ) + 2
            worksheet.set_column(idx, idx, max_length)
            
        # تنسيق الرأس
        header_format = writer.book.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
    print(f"تم إنشاء قالب المصاريف في: {template_path}")
    return str(template_path)  # تحويل المسار إلى نص

if __name__ == '__main__':
    create_expense_template() 