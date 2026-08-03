from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, BooleanField, DateField, FloatField
from wtforms.validators import DataRequired, NumberRange, Optional
from app.models.destination import Destination


class ItineraryStep1Form(FlaskForm):
    """创建行程第一步：基本信息"""
    destination_id = SelectField('目的地', coerce=int, validators=[
        DataRequired(message='请选择目的地')
    ])
    days_count = IntegerField('行程天数', validators=[
        DataRequired(message='请输入行程天数'),
        NumberRange(min=1, max=30, message='行程天数必须在1-30天之间')
    ])
    budget_level = SelectField('预算等级', choices=[
        ('经济', '经济型'),
        ('舒适', '舒适型'),
        ('豪华', '豪华型')
    ], validators=[DataRequired(message='请选择预算等级')])

    def __init__(self, *args, **kwargs):
        super(ItineraryStep1Form, self).__init__(*args, **kwargs)
        # 动态加载目的地选项
        destinations = Destination.query.all()
        self.destination_id.choices = [(d.id, f"{d.name} - {d.city}") for d in destinations]


class ItineraryStep2Form(FlaskForm):
    """创建行程第二步：兴趣标签和补充说明"""
    title = StringField('行程标题', validators=[
        DataRequired(message='请输入行程标题')
    ])
    interest_tags = StringField('兴趣标签（用逗号分隔）', validators=[
        Optional()
    ])
    additional_notes = TextAreaField('补充说明', validators=[
        Optional()
    ])
    is_public = BooleanField('公开行程')


class ItineraryEditForm(FlaskForm):
    """行程编辑表单"""
    title = StringField('行程标题', validators=[
        DataRequired(message='请输入行程标题')
    ])
    days_count = IntegerField('行程天数', validators=[
        DataRequired(message='请输入行程天数'),
        NumberRange(min=1, max=30, message='行程天数必须在1-30天之间')
    ])
    budget_level = SelectField('预算等级', choices=[
        ('经济', '经济型'),
        ('舒适', '舒适型'),
        ('豪华', '豪华型')
    ], validators=[DataRequired(message='请选择预算等级')])
    interest_tags = StringField('兴趣标签（用逗号分隔）', validators=[Optional()])
    is_public = BooleanField('公开行程')


class DayActivityForm(FlaskForm):
    """活动编辑表单"""
    activity_type = SelectField('活动类型', choices=[
        ('景点', '景点'),
        ('餐厅', '餐厅'),
        ('交通', '交通'),
        ('住宿', '住宿')
    ], validators=[DataRequired(message='请选择活动类型')])
    name = StringField('活动名称', validators=[
        DataRequired(message='请输入活动名称')
    ])
    description = TextAreaField('活动描述', validators=[Optional()])
    location = StringField('地点/地址', validators=[Optional()])
    duration_minutes = IntegerField('预计时长（分钟）', validators=[
        Optional(),
        NumberRange(min=1, message='时长必须大于0')
    ])
    estimated_cost = FloatField('预估费用', validators=[
        Optional(),
        NumberRange(min=0, message='费用不能为负数')
    ])
    tip = TextAreaField('小贴士', validators=[Optional()])
    order_index = IntegerField('顺序', validators=[
        DataRequired(message='请输入顺序'),
        NumberRange(min=0, message='顺序不能为负数')
    ])