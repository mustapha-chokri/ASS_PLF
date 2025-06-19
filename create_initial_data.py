from app import create_app, db
from app.models.student import EducationalLevel

def create_initial_data():
    # Configurar la aplicación y el contexto
    app = create_app()
    with app.app_context():
        # Crear niveles educativos si no existen
        create_educational_levels()
        print("Datos iniciales creados con éxito.")

def create_educational_levels():
    # Lista de niveles educativos con su orden
    levels = [
        {"name": "تمهيدي", "order": 1},  # Preescolar
        {"name": "المستوى الأول", "order": 2},  # Primer nivel
        {"name": "المستوى الثاني", "order": 3},  # Segundo nivel
        {"name": "المستوى الثالث", "order": 4},  # Tercer nivel
        {"name": "المستوى الرابع", "order": 5},  # Cuarto nivel
        {"name": "المستوى الخامس", "order": 6},  # Quinto nivel
        {"name": "المستوى السادس", "order": 7},  # Sexto nivel
        {"name": "الإعدادي - السنة الأولى", "order": 8},  # Secundaria - Primer año
        {"name": "الإعدادي - السنة الثانية", "order": 9},  # Secundaria - Segundo año
        {"name": "الإعدادي - السنة الثالثة", "order": 10},  # Secundaria - Tercer año
        {"name": "الثانوي - الجذع المشترك", "order": 11},  # Bachillerato - Tronco común
        {"name": "الثانوي - السنة الأولى", "order": 12},  # Bachillerato - Primer año
        {"name": "الثانوي - السنة الثانية (باك)", "order": 13},  # Bachillerato - Segundo año (Bac)
        {"name": "جامعي", "order": 14},  # Universidad
    ]
    
    # Verificar si ya hay niveles existentes
    if EducationalLevel.query.count() > 0:
        print("Ya existen niveles educativos en la base de datos.")
        return
    
    # Crear y guardar los niveles educativos
    for level_data in levels:
        level = EducationalLevel(
            name=level_data["name"],
            order=level_data["order"]
        )
        db.session.add(level)
    
    db.session.commit()
    print(f"Se han creado {len(levels)} niveles educativos.")

if __name__ == "__main__":
    create_initial_data() 