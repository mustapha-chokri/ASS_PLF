import pandas as pd
import os

def create_income_template():
    # إنشاء DataFrame مع الأعمدة المطلوبة
    df = pd.DataFrame(columns=[
        'العملية',
        'المبلغ',
        'التاريخ',
        'نوع الدفع',
        'المصدر',
        'المسؤول',
        'ملاحظات'
    ])
    
    # إضافة مثال للبيانات
    example_data = {
        'العملية': ['بيع منتجات', 'إيجار'],
        'المبلغ': [1000, 500],
        'التاريخ': ['2024-03-20', '2024-03-21'],
        'نوع الدفع': ['نقدي', 'تحويل بنكي'],
        'المصدر': ['مبيعات', 'إيجارات'],
        'المسؤول': ['admin', 'admin'],
        'ملاحظات': ['بيع منتجات متنوعة', 'إيجار محل']
    }
    df = pd.DataFrame(example_data)
    
    # إنشاء مجلد templates إذا لم يكن موجوداً
    templates_dir = os.path.join('app', 'static', 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # حفظ الملف
    output_path = os.path.join(templates_dir, 'income_template.xlsx')
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='المداخيل', index=False)
        workbook = writer.book
        worksheet = writer.sheets['المداخيل']
        
        # تنسيق الرأس
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'align': 'center',
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        # تنسيق الخلايا
        cell_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'align': 'right',
            'border': 1
        })
        
        # تطبيق التنسيق على الرأس
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
        
        # تطبيق التنسيق على البيانات
        for row_num in range(len(df)):
            for col_num in range(len(df.columns)):
                worksheet.write(row_num + 1, col_num, df.iloc[row_num, col_num], cell_format)
        
        # إضافة تعليمات
        worksheet.write(len(df) + 2, 0, 'تعليمات:', header_format)
        worksheet.write(len(df) + 3, 0, '1. يجب أن تكون جميع الأعمدة موجودة في الملف', cell_format)
        worksheet.write(len(df) + 4, 0, '2. يجب أن يكون المبلغ رقماً', cell_format)
        worksheet.write(len(df) + 5, 0, '3. يجب أن يكون التاريخ بتنسيق YYYY-MM-DD', cell_format)
        worksheet.write(len(df) + 6, 0, '4. يجب أن يكون المسؤول موجوداً في النظام', cell_format)
    
    print(f"تم إنشاء قالب المداخيل في: {output_path}")

if __name__ == '__main__':
    create_income_template() 