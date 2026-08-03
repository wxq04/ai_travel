from flask import render_template, current_app
from typing import Dict, Optional
import io
from app.services.ai_service import ai_service
from datetime import datetime

# 尝试导入 WeasyPrint，如果失败则标记不可用
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False


class PDFService:
    """
    PDF 导出服务
    先调用 ai_service.generate_summary 生成摘要
    渲染 PDF 专用 HTML 模板（含标题、摘要、每日时间轴、费用汇总表）
    使用 WeasyPrint 将 HTML 转为 PDF 字节流返回
    """

    def __init__(self):
        self.pdf_template = 'itineraries/pdf_template.html'
        self.available = WEASYPRINT_AVAILABLE

    def generate_pdf(self, itinerary_data: Dict, itinerary_title: str,
                     destination_name: str, author_name: str) -> Optional[bytes]:
        """
        生成行程 PDF
        
        Args:
            itinerary_data: 行程数据（包含 days 列表）
            itinerary_title: 行程标题
            destination_name: 目的地名称
            author_name: 作者名称
        
        Returns:
            PDF 字节流
        """
        if not self.available:
            current_app.logger.error('PDF 导出功能不可用：WeasyPrint 未安装')
            return None
            
        try:
            # 生成行程摘要
            summary = None
            if ai_service:
                try:
                    summary = ai_service.generate_summary(itinerary_data)
                except Exception as e:
                    current_app.logger.error(f'生成摘要失败: {str(e)}')
                    summary = self._generate_default_summary(itinerary_data)

            if not summary:
                summary = self._generate_default_summary(itinerary_data)

            # 计算总费用
            total_cost = self._calculate_total_cost(itinerary_data)

            # 准备 PDF 数据
            pdf_data = {
                'title': itinerary_title,
                'destination': destination_name,
                'author': author_name,
                'summary': summary,
                'days': itinerary_data.get('days', []),
                'total_cost': total_cost,
                'generated_at': datetime.now().strftime('%Y年%m月%d日'),
                'days_count': len(itinerary_data.get('days', []))
            }

            # 渲染 HTML 模板
            html_content = render_template(self.pdf_template, **pdf_data)

            # 使用 WeasyPrint 转换为 PDF
            pdf_bytes = HTML(string=html_content).write_pdf()

            return pdf_bytes

        except Exception as e:
            current_app.logger.error(f'生成 PDF 失败: {str(e)}')
            return None

    def _generate_default_summary(self, itinerary_data: Dict) -> str:
        """生成默认摘要（当 AI 服务不可用时）"""
        days_count = len(itinerary_data.get('days', []))
        
        # 统计活动类型
        activities_count = 0
        attractions = []
        restaurants = []

        for day in itinerary_data.get('days', []):
            for activity in day.get('activities', []):
                activities_count += 1
                if activity.get('type') == '景点':
                    attractions.append(activity.get('name'))
                elif activity.get('type') == '餐厅':
                    restaurants.append(activity.get('name'))

        summary = f"这是一次精彩的{days_count}日旅行，共包含{activities_count}个精心安排的活动。"
        
        if attractions:
            summary += f"您将游览{len(attractions)}个特色景点，"
        
        if restaurants:
            summary += f"品尝{len(restaurants)}道当地美食。"
        
        summary += "让这次旅程成为难忘的回忆。"

        return summary

    def _calculate_total_cost(self, itinerary_data: Dict) -> float:
        """计算总费用"""
        total_cost = 0.0

        for day in itinerary_data.get('days', []):
            for activity in day.get('activities', []):
                cost = activity.get('cost', 0)
                if cost:
                    total_cost += float(cost)

        return total_cost

    def generate_pdf_filename(self, itinerary_title: str) -> str:
        """生成 PDF 文件名"""
        # 清理标题中的特殊字符
        safe_title = itinerary_title.replace('/', '_').replace('\\', '_').replace(':', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{safe_title}_{timestamp}.pdf"

    def get_pdf_with_weather(self, itinerary_data: Dict, itinerary_title: str,
                            destination_name: str, author_name: str,
                            weather_data: Optional[Dict] = None) -> Optional[bytes]:
        """
        生成包含天气信息的 PDF
        
        Args:
            itinerary_data: 行程数据
            itinerary_title: 行程标题
            destination_name: 目的地名称
            author_name: 作者名称
            weather_data: 天气数据（可选）
        
        Returns:
            PDF 字节流
        """
        if not self.available:
            current_app.logger.error('PDF 导出功能不可用：WeasyPrint 未安装')
            return None
            
        try:
            # 如果有天气数据，添加到行程数据中
            if weather_data:
                for i, day in enumerate(itinerary_data.get('days', [])):
                    if i < len(weather_data):
                        day['weather'] = weather_data[i]

            # 调用标准 PDF 生成方法
            return self.generate_pdf(itinerary_data, itinerary_title,
                                     destination_name, author_name)

        except Exception as e:
            current_app.logger.error(f'生成带天气的 PDF 失败: {str(e)}')
            return None


# 全局 PDF 服务实例
pdf_service = None


def init_pdf_service(app=None):
    """初始化 PDF 服务"""
    global pdf_service
    # 在初始化时记录状态
    if app:
        if WEASYPRINT_AVAILABLE:
            app.logger.info('WeasyPrint 已加载，PDF 导出功能可用')
        else:
            app.logger.warning('WeasyPrint 不可用，PDF 导出功能将被禁用')
    pdf_service = PDFService()
    return pdf_service