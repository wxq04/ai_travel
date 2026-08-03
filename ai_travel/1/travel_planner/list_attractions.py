from app import create_app
from app.models.attraction import Attraction

app = create_app()
with app.app_context():
    attrs = Attraction.query.all()
    for a in attrs:
        print(f'{a.id}|{a.name}|{a.image_url}')
