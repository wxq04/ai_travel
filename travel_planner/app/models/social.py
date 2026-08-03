from datetime import datetime
from app.extensions import db


class Comment(db.Model):
    """评论表"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # 支持一级回复
    rating = db.Column(db.Integer)  # 评分 1-5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'itinerary_id', name='unique_user_like'),
    )

    def __repr__(self):
        return f'<Like User:{self.user_id} Itinerary:{self.itinerary_id}>'


class Favorite(db.Model):
    """收藏表"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'itinerary_id', name='unique_user_favorite'),
    )

    def __repr__(self):
        return f'<Favorite User:{self.user_id} Itinerary:{self.itinerary_id}>'


class Tag(db.Model):
    """标签表"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50))  # 标签分类
    icon = db.Column(db.String(50))  # 图标名称

    def __repr__(self):
        return f'<Tag {self.name}>'