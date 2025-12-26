"""数据导入导出服务"""
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import inspect, text
from app import db
from app.models import (
    User, Question, ExamPaper, ExamPaperQuestion,
    ExamSession, ExamResult, PracticeRecord, WrongQuestion, StudyStatistics
)


class DataService:
    """数据导入导出服务类"""
    
    # 定义导出顺序（考虑外键依赖关系）
    EXPORT_ORDER = [
        User,
        Question,
        ExamPaper,
        ExamPaperQuestion,
        ExamSession,
        ExamResult,
        PracticeRecord,
        WrongQuestion,
        StudyStatistics
    ]
    
    @staticmethod
    def _serialize_model(instance) -> Dict[str, Any]:
        """将模型实例序列化为字典
        
        Args:
            instance: SQLAlchemy 模型实例
            
        Returns:
            序列化后的字典
        """
        result = {}
        mapper = inspect(instance.__class__)
        
        for column in mapper.columns:
            value = getattr(instance, column.name)
            
            # 处理特殊类型
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif value is None:
                result[column.name] = None
            else:
                result[column.name] = value
        
        return result
    
    @staticmethod
    def export_to_json(models: Optional[List[type]] = None) -> str:
        """导出数据为 JSON 格式
        
        Args:
            models: 要导出的模型列表，如果为 None 则导出所有模型
            
        Returns:
            JSON 格式的字符串
        """
        if models is None:
            models = DataService.EXPORT_ORDER
        
        export_data = {
            'metadata': {
                'export_time': datetime.utcnow().isoformat(),
                'version': '1.0.0'
            },
            'data': {}
        }
        
        for model in models:
            table_name = model.__tablename__
            instances = model.query.all()
            export_data['data'][table_name] = [
                DataService._serialize_model(instance) for instance in instances
            ]
        
        return json.dumps(export_data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def export_to_sql(models: Optional[List[type]] = None) -> str:
        """导出数据为 SQL INSERT 语句
        
        Args:
            models: 要导出的模型列表，如果为 None 则导出所有模型
            
        Returns:
            SQL INSERT 语句字符串
        """
        if models is None:
            models = DataService.EXPORT_ORDER
        
        sql_statements = []
        sql_statements.append('-- 数据导出')
        sql_statements.append(f'-- 导出时间: {datetime.utcnow().isoformat()}')
        sql_statements.append('-- 版本: 1.0.0')
        sql_statements.append('')
        
        for model in models:
            table_name = model.__tablename__
            instances = model.query.all()
            
            if not instances:
                continue
            
            sql_statements.append(f'-- 表: {table_name}')
            
            for instance in instances:
                data = DataService._serialize_model(instance)
                columns = ', '.join(data.keys())
                
                # 构建值列表，正确处理字符串和 NULL
                values = []
                mapper = inspect(instance.__class__)
                column_types = {col.name: col.type for col in mapper.columns}
                
                for key, value in data.items():
                    if value is None:
                        values.append('NULL')
                    elif isinstance(value, str):
                        # 转义单引号
                        escaped_value = value.replace("'", "''")
                        values.append(f"'{escaped_value}'")
                    elif isinstance(value, bool):
                        values.append('1' if value else '0')
                    elif isinstance(value, (dict, list)):
                        # JSON 字段：序列化为 JSON 字符串
                        json_str = json.dumps(value, ensure_ascii=False)
                        escaped_json = json_str.replace("'", "''")
                        values.append(f"'{escaped_json}'")
                    else:
                        values.append(str(value))
                
                values_str = ', '.join(values)
                sql_statements.append(
                    f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});"
                )
            
            sql_statements.append('')
        
        return '\n'.join(sql_statements)
    
    @staticmethod
    def _deserialize_model(model_class: type, data: Dict[str, Any]):
        """将字典反序列化为模型实例
        
        Args:
            model_class: 模型类
            data: 数据字典
            
        Returns:
            模型实例
        """
        instance = model_class()
        mapper = inspect(model_class)
        
        for column in mapper.columns:
            if column.name in data:
                value = data[column.name]
                
                # 处理日期时间类型
                if value is not None and column.type.python_type == datetime:
                    if isinstance(value, str):
                        value = datetime.fromisoformat(value)
                
                setattr(instance, column.name, value)
        
        return instance
    
    @staticmethod
    def import_from_json(json_data: str, clear_existing: bool = False) -> Dict[str, int]:
        """从 JSON 格式导入数据
        
        Args:
            json_data: JSON 格式的数据字符串
            clear_existing: 是否清空现有数据
            
        Returns:
            导入统计信息字典 {table_name: count}
        """
        data = json.loads(json_data)
        import_stats = {}
        
        # 如果需要清空现有数据
        if clear_existing:
            for model in reversed(DataService.EXPORT_ORDER):
                model.query.delete()
            db.session.commit()
        
        # 按顺序导入数据
        for model in DataService.EXPORT_ORDER:
            table_name = model.__tablename__
            
            if table_name not in data.get('data', {}):
                continue
            
            records = data['data'][table_name]
            count = 0
            
            for record_data in records:
                instance = DataService._deserialize_model(model, record_data)
                db.session.add(instance)
                count += 1
            
            import_stats[table_name] = count
        
        db.session.commit()
        return import_stats
    
    @staticmethod
    def import_from_sql(sql_data: str) -> Dict[str, int]:
        """从 SQL INSERT 语句导入数据
        
        Args:
            sql_data: SQL INSERT 语句字符串
            
        Returns:
            导入统计信息字典 {table_name: count}
        """
        import_stats = {}
        
        # 解析 SQL 语句
        lines = sql_data.strip().split('\n')
        current_table = None
        
        for line in lines:
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('--'):
                # 尝试提取表名
                if line.startswith('-- 表:'):
                    current_table = line.split(':', 1)[1].strip()
                    if current_table not in import_stats:
                        import_stats[current_table] = 0
                continue
            
            # 执行 INSERT 语句
            if line.upper().startswith('INSERT'):
                try:
                    db.session.execute(text(line))
                    if current_table:
                        import_stats[current_table] = import_stats.get(current_table, 0) + 1
                except Exception as e:
                    db.session.rollback()
                    raise Exception(f"导入 SQL 失败: {line[:50]}... 错误: {str(e)}")
        
        db.session.commit()
        return import_stats
