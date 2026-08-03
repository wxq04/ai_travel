from datetime import datetime
from app.extensions import db
import json


class Destination(db.Model):
    """目的地表"""
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    country = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    images = db.Column(db.Text)  # JSON 数组存储多张图片
    best_season = db.Column(db.String(50))  # 最佳旅游季节
    category = db.Column(db.String(20), nullable=False)  # 自然/历史/美食/都市/海滨
    avg_rating = db.Column(db.Float, default=0.0)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    itineraries = db.relationship('Itinerary', backref='destination', lazy='dynamic')

    def get_images(self):
        """获取图片列表"""
        if self.images:
            try:
                return json.loads(self.images)
            except json.JSONDecodeError:
                return []
        return []

    def set_images(self, images_list):
        """设置图片列表"""
        if isinstance(images_list, list):
            self.images = json.dumps(images_list, ensure_ascii=False)
        else:
            self.images = json.dumps([], ensure_ascii=False)

    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()

    def update_avg_rating(self):
        """更新平均评分"""
        from app.models.social import Comment
        comments = Comment.query.filter_by(destination_id=self.id).all()
        if comments:
            total_rating = sum(c.rating for c in comments if c.rating)
            count = sum(1 for c in comments if c.rating)
            if count > 0:
                self.avg_rating = round(total_rating / count, 1)
        else:
            self.avg_rating = 0.0
        db.session.commit()

    def __repr__(self):
        return f'<Destination {self.name}>'