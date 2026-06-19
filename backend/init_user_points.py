"""初始化用户积分记录

为所有现有用户创建积分记录
"""
from app import create_app, db
from app.models.user import User
from app.models.achievement import UserPoints

def init_user_points():
    """为所有用户初始化积分记录"""
    app = create_app()
    
    with app.app_context():
        # 获取所有用户
        users = User.query.all()
        
        print(f'找到 {len(users)} 个用户')
        
        created_count = 0
        existing_count = 0
        
        for user in users:
            # 检查是否已有积分记录
            user_points = UserPoints.query.filter_by(user_id=user.id).first()
            
            if not user_points:
                # 创建新的积分记录
                user_points = UserPoints(
                    user_id=user.id,
                    total_points=0,
                    current_level=1,
                    streak_days=0,
                    last_activity_date=None
                )
                db.session.add(user_points)
                created_count += 1
                print(f'为用户 {user.username} (ID: {user.id}) 创建积分记录')
            else:
                existing_count += 1
                print(f'用户 {user.username} (ID: {user.id}) 已有积分记录')
        
        # 提交更改
        db.session.commit()
        
        print('\n' + '=' * 50)
        print('初始化完成！')
        print(f'创建新记录: {created_count}')
        print(f'已存在记录: {existing_count}')
        print('=' * 50)

if __name__ == '__main__':
    init_user_points()
