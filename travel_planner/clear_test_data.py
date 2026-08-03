# -*- coding: utf-8 -*-
from app import create_app
from app.extensions import db
from app.models.itinerary import Itinerary, ItineraryDay, DayActivity

app = create_app()
with app.app_context():
    # 删除旧的测试行程
    old_itineraries = Itinerary.query.all()
    print(f'删除 {len(old_itineraries)} 个旧行程...')
    for it in old_itineraries:
        db.session.delete(it)
    db.session.commit()
    print('已清理旧数据')
