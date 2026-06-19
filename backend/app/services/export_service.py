"""
笔记导出服务

提供笔记导出为 PDF 和 Markdown 格式的功能
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import tempfile
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import markdown

from app.models.note import QuestionNote
from app.models.question import Question
from app import db


class ExportService:
    """笔记导出服务类"""
    
    def __init__(self):
        """初始化导出服务"""
        self._register_fonts()
    
    def _register_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册系统中文字体
            # Windows: SimSun (宋体)
            # Linux: 需要安装中文字体
            font_paths = [
                'C:/Windows/Fonts/simsun.ttc',  # Windows 宋体
                'C:/Windows/Fonts/msyh.ttc',    # Windows 微软雅黑
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # Linux 文泉驿
                '/System/Library/Fonts/PingFang.ttc',  # macOS
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Chinese', font_path))
                        return
                    except Exception:
                        continue
        except Exception as e:
            print(f"字体注册失败: {e}")
    
    def export_notes_to_pdf(
        self,
        user_id: int,
        note_ids: Optional[List[int]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> BytesIO:
        """
        导出笔记为 PDF
        
        Args:
            user_id: 用户ID
            note_ids: 笔记ID列表（可选）
            filters: 筛选条件（可选）
                - subject: 科目
                - chapter: 章节
                - start_date: 开始日期
                - end_date: 结束日期
        
        Returns:
            BytesIO: PDF 文件流
        """
        # 获取笔记列表
        notes = self._get_notes_for_export(user_id, note_ids, filters)
        
        if not notes:
            raise ValueError("没有可导出的笔记")
        
        # 创建 PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # 构建内容
        story = []
        styles = self._get_pdf_styles()
        
        # 添加标题
        title = Paragraph("我的笔记", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))
        
        # 添加导出信息
        export_info = f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        export_info += f"笔记数量: {len(notes)}"
        info_para = Paragraph(export_info, styles['Normal'])
        story.append(info_para)
        story.append(Spacer(1, 0.3 * inch))
        
        # 添加每条笔记
        for i, note in enumerate(notes, 1):
            # 笔记标题
            note_title = f"笔记 {i}"
            if note.question:
                note_title += f" - {note.question.subject}"
                if note.question.chapter:
                    note_title += f" / {note.question.chapter}"
            
            title_para = Paragraph(note_title, styles['Heading1'])
            story.append(title_para)
            story.append(Spacer(1, 0.1 * inch))
            
            # 笔记元信息
            meta_info = f"题目ID: {note.question_id}<br/>"
            meta_info += f"创建时间: {note.created_at.strftime('%Y-%m-%d %H:%M')}<br/>"
            if note.updated_at:
                meta_info += f"更新时间: {note.updated_at.strftime('%Y-%m-%d %H:%M')}"
            
            meta_para = Paragraph(meta_info, styles['Meta'])
            story.append(meta_para)
            story.append(Spacer(1, 0.1 * inch))
            
            # 笔记内容（转换 Markdown 为 HTML）
            content_html = self._markdown_to_html(note.content)
            # 简化 HTML 标签以适应 ReportLab
            content_html = self._simplify_html_for_pdf(content_html)
            
            content_para = Paragraph(content_html, styles['Content'])
            story.append(content_para)
            story.append(Spacer(1, 0.3 * inch))
            
            # 每条笔记后添加分隔线
            if i < len(notes):
                story.append(Spacer(1, 0.1 * inch))
        
        # 生成 PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def export_notes_to_markdown(
        self,
        user_id: int,
        note_ids: Optional[List[int]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        导出笔记为 Markdown
        
        Args:
            user_id: 用户ID
            note_ids: 笔记ID列表（可选）
            filters: 筛选条件（可选）
        
        Returns:
            str: Markdown 文本
        """
        # 获取笔记列表
        notes = self._get_notes_for_export(user_id, note_ids, filters)
        
        if not notes:
            raise ValueError("没有可导出的笔记")
        
        # 构建 Markdown 内容
        lines = []
        
        # 添加标题
        lines.append("# 我的笔记")
        lines.append("")
        lines.append(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"笔记数量: {len(notes)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 添加每条笔记
        for i, note in enumerate(notes, 1):
            # 笔记标题
            note_title = f"## 笔记 {i}"
            if note.question:
                note_title += f" - {note.question.subject}"
                if note.question.chapter:
                    note_title += f" / {note.question.chapter}"
            
            lines.append(note_title)
            lines.append("")
            
            # 笔记元信息
            lines.append(f"- **题目ID**: {note.question_id}")
            lines.append(f"- **创建时间**: {note.created_at.strftime('%Y-%m-%d %H:%M')}")
            if note.updated_at:
                lines.append(f"- **更新时间**: {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
            lines.append("")
            
            # 笔记内容
            lines.append("### 内容")
            lines.append("")
            lines.append(note.content)
            lines.append("")
            
            # 分隔线
            if i < len(notes):
                lines.append("---")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_download_link(
        self,
        user_id: int,
        export_format: str,
        note_ids: Optional[List[int]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成下载链接
        
        Args:
            user_id: 用户ID
            export_format: 导出格式（pdf/markdown）
            note_ids: 笔记ID列表（可选）
            filters: 筛选条件（可选）
        
        Returns:
            dict: 包含文件名和文件内容的字典
        """
        if export_format not in ['pdf', 'markdown']:
            raise ValueError("不支持的导出格式")
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"notes_export_{timestamp}.{export_format if export_format == 'pdf' else 'md'}"
        
        # 导出内容
        if export_format == 'pdf':
            content = self.export_notes_to_pdf(user_id, note_ids, filters)
            content_type = 'application/pdf'
        else:
            content = self.export_notes_to_markdown(user_id, note_ids, filters)
            content_type = 'text/markdown'
        
        return {
            'filename': filename,
            'content': content,
            'content_type': content_type
        }
    
    def _get_notes_for_export(
        self,
        user_id: int,
        note_ids: Optional[List[int]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[QuestionNote]:
        """
        获取要导出的笔记列表
        
        Args:
            user_id: 用户ID
            note_ids: 笔记ID列表（可选）
            filters: 筛选条件（可选）
        
        Returns:
            List[QuestionNote]: 笔记列表
        """
        query = QuestionNote.query.filter_by(
            user_id=user_id,
            is_deleted=False
        )
        
        # 如果指定了笔记ID列表
        if note_ids:
            query = query.filter(QuestionNote.id.in_(note_ids))
        
        # 应用筛选条件
        if filters:
            # 需要 join Question 表来筛选科目和章节
            query = query.join(Question, QuestionNote.question_id == Question.id)
            
            if filters.get('subject'):
                query = query.filter(Question.subject == filters['subject'])
            
            if filters.get('chapter'):
                query = query.filter(Question.chapter == filters['chapter'])
            
            if filters.get('start_date'):
                query = query.filter(QuestionNote.created_at >= filters['start_date'])
            
            if filters.get('end_date'):
                query = query.filter(QuestionNote.created_at <= filters['end_date'])
        
        # 按创建时间排序
        notes = query.order_by(QuestionNote.created_at.desc()).all()
        
        return notes
    
    def _get_pdf_styles(self) -> Dict[str, ParagraphStyle]:
        """
        获取 PDF 样式
        
        Returns:
            dict: 样式字典
        """
        styles = getSampleStyleSheet()
        
        # 尝试使用中文字体
        try:
            font_name = 'Chinese'
            pdfmetrics.getFont(font_name)
        except Exception:
            font_name = 'Helvetica'
        
        # 检查并添加样式（避免重复定义）
        if 'Title' not in styles:
            styles.add(ParagraphStyle(
                name='Title',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#333333',
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName=font_name
            ))
        
        if 'Heading1' not in styles or styles['Heading1'].fontSize != 16:
            # 修改现有样式而不是添加新样式
            styles['Heading1'].fontSize = 16
            styles['Heading1'].textColor = '#333333'
            styles['Heading1'].spaceAfter = 6
            styles['Heading1'].fontName = font_name
        
        if 'Meta' not in styles:
            styles.add(ParagraphStyle(
                name='Meta',
                parent=styles['Normal'],
                fontSize=9,
                textColor='#666666',
                spaceAfter=6,
                fontName=font_name
            ))
        
        if 'Content' not in styles:
            styles.add(ParagraphStyle(
                name='Content',
                parent=styles['Normal'],
                fontSize=11,
                textColor='#333333',
                spaceAfter=12,
                leading=16,
                fontName=font_name
            ))
        
        return styles
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        将 Markdown 转换为 HTML
        
        Args:
            markdown_text: Markdown 文本
        
        Returns:
            str: HTML 文本
        """
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite']
        )
        return html
    
    def _simplify_html_for_pdf(self, html: str) -> str:
        """
        简化 HTML 以适应 ReportLab
        
        ReportLab 只支持有限的 HTML 标签
        
        Args:
            html: HTML 文本
        
        Returns:
            str: 简化后的 HTML
        """
        # 移除不支持的标签
        import re
        
        # 保留基本标签：b, i, u, br, p
        # 移除其他标签但保留内容
        html = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'<b>\1</b><br/>', html)
        html = re.sub(r'<code>(.*?)</code>', r'<i>\1</i>', html)
        html = re.sub(r'<pre>(.*?)</pre>', r'<i>\1</i>', html, flags=re.DOTALL)
        html = re.sub(r'<blockquote>(.*?)</blockquote>', r'<i>\1</i>', html, flags=re.DOTALL)
        html = re.sub(r'<ul>(.*?)</ul>', r'\1', html, flags=re.DOTALL)
        html = re.sub(r'<ol>(.*?)</ol>', r'\1', html, flags=re.DOTALL)
        html = re.sub(r'<li>(.*?)</li>', r'• \1<br/>', html)
        
        return html
