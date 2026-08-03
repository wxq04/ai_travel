from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, FileField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User
import re


class RegistrationForm(FlaskForm):
    """用户注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=3, max=80, message='用户名长度必须在3-80个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, max=20, message='密码长度必须在6-20个字符之间')
    ])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次密码必须一致')
    ])

    def validate_username(self, field):
        """验证用户名是否已存在"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')

    def validate_email(self, field):
        """验证邮箱是否已存在"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')


class LoginForm(FlaskForm):
    """用户登录表单"""
    username_or_email = StringField('用户名/邮箱', validators=[
        DataRequired(message='请输入用户名或邮箱')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空')
    ])
    remember_me = BooleanField('记住我（30天）')


class ProfileForm(FlaskForm):
    """个人资料编辑表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=3, max=80, message='用户名长度必须在3-80个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址')
    ])
    bio = TextAreaField('个人简介', validators=[
        Length(max=500, message='简介不能超过500个字符')
    ])
    avatar = FileField('头像')
    preference_tags = SelectMultipleField('兴趣标签', choices=[
        ('美食', '美食'),
        ('历史', '历史'),
        ('自然', '自然'),
        ('都市', '都市'),
        ('海滨', '海滨'),
        ('文化', '文化'),
        ('购物', '购物'),
        ('运动', '运动')
    ])

    def validate_username(self, field):
        """验证用户名是否已被其他人使用"""
        from flask_login import current_user
        if field.data != current_user.username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('该用户名已被使用')

    def validate_email(self, field):
        """验证邮箱是否已被其他人使用"""
        from flask_login import current_user
        if field.data != current_user.email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('该邮箱已被注册')


class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    old_password = PasswordField('原密码', validators=[
        DataRequired(message='请输入原密码')
    ])
    new_password = PasswordField('新密码', validators=[
        DataRequired(message='请输入新密码'),
        Length(min=6, max=20, message='密码长度必须在6-20个字符之间')
    ])
    new_password2 = PasswordField('确认新密码', validators=[
        DataRequired(message='请确认新密码'),
        EqualTo('new_password', message='两次密码必须一致')
    ])