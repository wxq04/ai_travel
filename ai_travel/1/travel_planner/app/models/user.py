from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db
import json


class User(UserMixin, db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), default='default_avatar.png')
    bio = db.Column(db.Text)
    preference_tags = db.Column(db.Text)  # JSON 格式存储用户偏好标签
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # 关系
    itineraries = db.relationship('Itinerary', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def get_preference_tags(self):
        """获取用户偏好标签列表"""
        if self.preference_tags:
            try:
                return json.loads(self.preference_tags)
            except json.JSONDecodeError:
                return []
        return []

    def set_preference_tags(self, tags_list):
        """设置用户偏好标签"""
        if isinstance(tags_list, list):
            self.preference_tags = json.dumps(tags_list, ensure_ascii=False)
        else:
            self.preference_tags = json.dumps([], ensure_ascii=False)

    def __repr__(self):
        return f'<User {self.username}>'