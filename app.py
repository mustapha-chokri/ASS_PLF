from app import create_app

app = create_app()
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # ساعة كاملة
app.config['WTF_CSRF_ENABLED'] = False  # تعطيل CSRF مؤقتًا للتشخيص

if __name__ == '__main__':
    app.run(debug=True)