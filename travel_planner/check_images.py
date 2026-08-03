from app import create_app
from app.models.destination import Destination

app = create_app('development')
with app.app_context():
    destinations = Destination.query.all()
    for d in destinations:
        print(f"{d.name}: {d.cover_image}")