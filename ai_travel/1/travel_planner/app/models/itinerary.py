from datetime import datetime
from app.extensions import db
import json


class Itinerary(db.Model):
    """主行程表"""
    __tablename__ = 'itineraries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    days_count = db.Column(db.Integer, default=1)
    budget_level = db.Column(db.String(20), default='舒适')  # 经济/舒适/豪华
    interest_tags = db.Column(db.Text)  # JSON 格式存储兴趣标签
    is_public = db.Column(db.Boolean, default=True)
    ai_generated = db.Column(db.Boolean, default=False)  # 是否由 AI 生成
    like_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    days = db.relationship('ItineraryDay', backref='itinerary', lazy='dynamic', 
                           cascade='all, delete-orphan', order_by='ItineraryDay.day_number')

    def get_interest_tags(self):
        """获取兴趣标签列表"""
        if self.interest_tags:
            try:
                return json.loads(self.interest_tags)
            except json.JSONDecodeError:
                return []
        return []

    def set_interest_tags(self, tags_list):
        """设置兴趣标签"""
        if isinstance(tags_list, list):
            self.interest_tags = json.dumps(tags_list, ensure_ascii=False)
        else:
            self.interest_tags = json.dumps([], ensure_ascii=False)

    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()

    def increment_like_count(self):
        """增加点赞数"""
        self.like_count += 1
        db.session.commit()

    def decrement_like_count(self):
        """减少点赞数"""
        if self.like_count > 0:
            self.like_count -= 1
            db.session.commit()

    def __repr__(self):
        return f'<Itinerary {self.title}>'


class ItineraryDay(db.Model):
    """行程天数表"""
    __tablename__ = 'itinerary_days'

    id = db.Column(db.Integer, primary_key=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False, index=True)
    day_number = db.Column(db.Integer, nullable=False)  # 第几天
    date = db.Column(db.Date)  # 具体日期
    theme = db.Column(db.String(100))  # 当天主题
    notes = db.Column(db.Text)  # 备注

    # 关系
    activities = db.relationship('DayActivity', backref='day', lazy='dynamic',
                                 cascade='all, delete-orphan', order_by='DayActivity.order_index')

    def __repr__(self):
        return f'<ItineraryDay Day {self.day_number}>'


class DayActivity(db.Model):
    """活动表"""
    __tablename__ = 'day_activities'

    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey('itinerary_days.id'), nullable=False, index=True)
    order_index = db.Column(db.Integer, default=0)  # 活动顺序
    activity_type = db.Column(db.String(20), nullable=False)  # 景点/餐厅/交通/住宿
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))  # 地点/地址
    duration_minutes = db.Column(db.Integer)  # 预计时长（分钟）
    estimated_cost = db.Column(db.Float)  # 预估费用
    tip = db.Column(db.Text)  # 小贴士
    image_url = db.Column(db.String(255))

    # 地理位置（从景点详情或地理编码获取）
    latitude = db.Column(db.Float)  # 纬度
    longitude = db.Column(db.Float)  # 经度

    def __repr__(self):
        return f'<DayActivity {self.name}>'