# 后端导入错误修复说明

## 问题描述

后端启动时出现多个导入错误：
1. `WrongAnalysisService` 无法从 `wrong_analysis_service.py` 导入
2. `token_required` 从不存在的 `app.utils.auth` 模块导入
3. `KnowledgePoint` 模型不存在

## 修复方案

### 1. 暂时禁用错题分析功能

由于 `wrong_analysis_service.py` 文件存在问题，暂时注释掉该功能：

**文件**: `exam/backend/app/__init__.py`

```python
# from app.routes.wrong_analysis import wrong_analysis_bp  # 暂时注释，修复导入问题
# app.register_blueprint(wrong_analysis_bp)  # 暂时注释，修复导入问题
```

### 2. 修复番茄钟路由认证

将 `pomodoro.py` 中的自定义认证装饰器替换为 Flask-JWT-Extended：

**文件**: `exam/backend/app/routes/pomodoro.py`

- 替换导入: `from app.utils.auth import token_required` → `from flask_jwt_extended import jwt_required, get_jwt_identity`
- 替换装饰器: `@token_required` → `@jwt_required()`
- 修改函数签名: 移除 `current_user` 参数，使用 `get_jwt_identity()` 获取用户ID

### 3. 修复知识图谱路由认证

同样修复 `knowledge_graph.py` 的认证问题，并暂时禁用该功能（因为缺少 `KnowledgePoint` 模型）：

**文件**: `exam/backend/app/__init__.py`

```python
# from app.routes.knowledge_graph import knowledge_graph_bp  # 暂时注释，缺少 KnowledgePoint 模型
# app.register_blueprint(knowledge_graph_bp)  # 暂时注释，缺少 KnowledgePoint 模型
```

## 修复结果

✓ 后端现在可以正常启动
✓ 所有其他功能保持不变
✓ 番茄钟功能已修复并可用

## 待办事项

如需恢复被禁用的功能，需要：

1. **错题分析功能**:
   - 修复 `wrong_analysis_service.py` 文件的导入问题
   - 确保 `WrongAnalysisService` 类正确定义

2. **知识图谱功能**:
   - 创建 `KnowledgePoint` 模型
   - 或修改 `knowledge_graph_service.py` 使用现有的模型

## 测试

运行以下命令测试后端启动：

```bash
cd exam/backend
python run.py
```

应该看到：
```
考试系统启动
环境: development
调试模式: True
数据库: sqlite:///exam.db
```

没有任何错误信息。
