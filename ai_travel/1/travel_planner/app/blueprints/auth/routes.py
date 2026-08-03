from datetime import timedelta
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.blueprints.auth import auth_bp
from app.extensions import db
from app.models.user import User
from app.models.itinerary import Itinerary
from app.blueprints.auth.forms import RegistrationForm, LoginForm, ProfileForm, ChangePasswordForm


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # 创建新用户
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        # 注册成功后自动登录
        login_user(user)
        flash('注册成功！欢迎加入旅行规划助手', 'success')
        return redirect(url_for('index'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # 支持用户名或邮箱登录
        username_or_email = form.username_or_email.data
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user is None or not user.check_password(form.password.data):
            flash('用户名/邮箱或密码错误', 'error')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('该账户已被禁用', 'error')
            return redirect(url_for('auth.login'))

        # 登录用户，支持"记住我"30天
        login_user(user, remember=form.remember_me.data, duration=timedelta(days=30))
        flash('登录成功！', 'success')

        # 获取 next 参数，登录后跳转
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """个人资料编辑"""
    form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if form.validate_on_submit():
        # 更新基本信息
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data

        # 更新偏好标签
        current_user.set_preference_tags(form.preference_tags.data)

        # 处理头像上传
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                current_user.avatar = filename
                flash('头像更新成功', 'success')

        db.session.commit()
        flash('个人资料更新成功', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', form=form, password_form=password_form)


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    password_form = ChangePasswordForm()

    if password_form.validate_on_submit():
        # 验证原密码
        if not current_user.check_password(password_form.old_password.data):
            flash('原密码错误', 'error')
            return redirect(url_for('auth.profile'))

        # 更新密码
        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('密码修改成功', 'success')
        return redirect(url_for('auth.profile'))

    flash('密码修改失败，请检查输入', 'error')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/user/<username>')
def user_profile(username):
    """用户主页（公开行程和简介）"""
    user = User.query.filter_by(username=username).first_or_404()

    # 获取用户的公开行程
    public_itineraries = Itinerary.query.filter_by(
        user_id=user.id,
        is_public=True
    ).order_by(Itinerary.created_at.desc()).limit(10).all()

    return render_template('auth/user_profile.html', user=user, itineraries=public_itineraries)