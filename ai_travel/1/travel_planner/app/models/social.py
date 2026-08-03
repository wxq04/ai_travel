from datetime import datetime
from app.extensions import db


def get_local_time():
    """获取当前本地时间"""
    return datetime.now()


class Comment(db.Model):
    """评论表"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # 支持一级回复
    rating = db.Column(db.Integer)  # 评分 1-5
    created_at = db.Column(db.DateTime, default=get_local_time)

    # 关系 - author 从 User.comments 的 backref 继承，replies 支持回复
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')

    def __repr__(self):
        return f'<Comment {self.id}>'


class Like(db.Model):
    """点赞表"""
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=get_local_time)

    # 联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'itinerary_id', name='unique_user_like'),
    )

    def __repr__(self):
        return f'<Like User:{self.user_id} Itinerary:{self.itinerary_id}>'


class Favorite(db.Model):
    """收藏行程表"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=get_local_time)

    # 联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'itinerary_id', name='unique_user_favorite'),
    )

    def __repr__(self):
        return f'<Favorite User:{self.user_id} Itinerary:{self.itinerary_id}>'


class SavedAttraction(db.Model):
    """用户收藏的景点表"""
    __tablename__ = 'saved_attractions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=get_local_time)

    # 联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'attraction_id', name='unique_user_saved_attraction'),
    )

    # 关系
    attraction = db.relationship('Attraction', backref='saved_by', lazy='joined')

    def __repr__(self):
        return f'<SavedAttraction User:{self.user_id} Attraction:{self.attraction_id}>'


class Tag(db.Model):
    """标签表"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50))  # 标签分类
    icon = db.Column(db.String(50))  # 图标名称

    def __repr__(self):
        return f'<Tag {self.name}>'