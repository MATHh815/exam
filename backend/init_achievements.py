"""成就系统初始化脚本

创建初始成就定义数据
"""
from app import create_app, db
from app.models.achievement import Achievement


# 成就定义数据
ACHIEVEMENTS = [
    # 学习类成就 (learning)
    {
        'name': '初学者',
        'description': '完成第一次练习',
        'icon': '🎯',
        'category': 'learning',
        'criteria': {'type': 'practice_count', 'value': 1},
        'points_reward': 10,
        'tier': 1
    },
    {
        'name': '勤奋学习',
        'description': '完成10次练习',
        'icon': '📚',
        'category': 'learning',
        'criteria': {'type': 'practice_count', 'value': 10},
        'points_reward': 50,
        'tier': 1
    },
    {
        'name': '学习达人',
        'description': '完成50次练习',
        'icon': '🏆',
        'category': 'learning',
        'criteria': {'type': 'practice_count', 'value': 50},
        'points_reward': 200,
        'tier': 2
    },
    {
        'name': '学习大师',
        'description': '完成100次练习',
        'icon': '👑',
        'category': 'learning',
        'criteria': {'type': 'practice_count', 'value': 100},
        'points_reward': 500,
        'tier': 3
    },
    {
        'name': '首次考试',
        'description': '完成第一次考试',
        'icon': '📝',
        'category': 'learning',
        'criteria': {'type': 'exam_count', 'value': 1},
        'points_reward': 20,
        'tier': 1
    },
    {
        'name': '考试专家',
        'description': '完成10次考试',
        'icon': '🎓',
        'category': 'learning',
        'criteria': {'type': 'exam_count', 'value': 10},
        'points_reward': 100,
        'tier': 2
    },
    {
        'name': '满分达成',
        'description': '获得一次满分（100分）',
        'icon': '💯',
        'category': 'learning',
        'criteria': {'type': 'perfect_score', 'value': 1},
        'points_reward': 100,
        'tier': 2
    },
    {
        'name': '高分选手',
        'description': '获得90分以上成绩10次',
        'icon': '⭐',
        'category': 'learning',
        'criteria': {'type': 'high_score_count', 'value': 10, 'threshold': 90},
        'points_reward': 150,
        'tier': 2
    },
    
    # 连续学习类成就 (streak)
    {
        'name': '坚持一天',
        'description': '连续学习1天',
        'icon': '🔥',
        'category': 'streak',
        'criteria': {'type': 'streak_days', 'value': 1},
        'points_reward': 5,
        'tier': 1
    },
    {
        'name': '三天打卡',
        'description': '连续学习3天',
        'icon': '🔥',
        'category': 'streak',
        'criteria': {'type': 'streak_days', 'value': 3},
        'points_reward': 20,
        'tier': 1
    },
    {
        'name': '一周坚持',
        'description': '连续学习7天',
        'icon': '🔥🔥',
        'category': 'streak',
        'criteria': {'type': 'streak_days', 'value': 7},
        'points_reward': 50,
        'tier': 2
    },
    {
        'name': '半月不辍',
        'description': '连续学习15天',
        'icon': '🔥🔥',
        'category': 'streak',
        'criteria': {'type': 'streak_days', 'value': 15},
        'points_reward': 100,
        'tier': 2
    },
    {
        'name': '月度坚持',
        'description': '连续学习30天',
        'icon': '🔥🔥🔥',
        'category': 'streak',
        'criteria': {'type': 'streak_days', 'value': 30},
        'points_reward': 300,
        'tier': 3
    },
    {
        'name': '百日筑基',
        'description': '连续学习100天',
        'icon': '👑🔥',
        'category': 'streak',
        'criteria': {'type': 'streak_days', 'value': 100},
        'points_reward': 1000,
        'tier': 3
    },
    
    # 里程碑类成就 (milestone)
    {
        'name': '新手上路',
        'description': '达到等级2',
        'icon': '🌟',
        'category': 'milestone',
        'criteria': {'type': 'level', 'value': 2},
        'points_reward': 50,
        'tier': 1
    },
    {
        'name': '渐入佳境',
        'description': '达到等级5',
        'icon': '🌟🌟',
        'category': 'milestone',
        'criteria': {'type': 'level', 'value': 5},
        'points_reward': 100,
        'tier': 2
    },
    {
        'name': '学有所成',
        'description': '达到等级10',
        'icon': '🌟🌟🌟',
        'category': 'milestone',
        'criteria': {'type': 'level', 'value': 10},
        'points_reward': 300,
        'tier': 3
    },
    {
        'name': '积分新手',
        'description': '累计获得100积分',
        'icon': '💰',
        'category': 'milestone',
        'criteria': {'type': 'total_points', 'value': 100},
        'points_reward': 20,
        'tier': 1
    },
    {
        'name': '积分富翁',
        'description': '累计获得1000积分',
        'icon': '💰💰',
        'category': 'milestone',
        'criteria': {'type': 'total_points', 'value': 1000},
        'points_reward': 100,
        'tier': 2
    },
    {
        'name': '积分大亨',
        'description': '累计获得5000积分',
        'icon': '💰💰💰',
        'category': 'milestone',
        'criteria': {'type': 'total_points', 'value': 5000},
        'points_reward': 500,
        'tier': 3
    },
    {
        'name': '笔记达人',
        'description': '创建10条笔记',
        'icon': '📝',
        'category': 'milestone',
        'criteria': {'type': 'note_count', 'value': 10},
        'points_reward': 50,
        'tier': 1
    },
    {
        'name': '收藏家',
        'description': '收藏50道题目',
        'icon': '⭐',
        'category': 'milestone',
        'criteria': {'type': 'bookmark_count', 'value': 50},
        'points_reward': 50,
        'tier': 1
    },
    {
        'name': '计划达人',
        'description': '完成一个学习计划',
        'icon': '📅',
        'category': 'milestone',
        'criteria': {'type': 'plan_completed', 'value': 1},
        'points_reward': 100,
        'tier': 2
    },
    {
        'name': '全能学霸',
        'description': '完成5个学习计划',
        'icon': '🎖️',
        'category': 'milestone',
        'criteria': {'type': 'plan_completed', 'value': 5},
        'points_reward': 500,
        'tier': 3
    },
]


def init_achievements():
    """初始化成就数据"""
    app = create_app()
    
    with app.app_context():
        print("开始初始化成就数据...")
        
        # 检查是否已经初始化
        existing_count = Achievement.query.count()
        if existing_count > 0:
            print(f"警告: 数据库中已存在 {existing_count} 个成就")
            response = input("是否清空并重新初始化? (yes/no): ")
            if response.lower() != 'yes':
                print("取消初始化")
                return
            
            # 清空现有成就
            Achievement.query.delete()
            db.session.commit()
            print("已清空现有成就数据")
        
        # 创建成就
        created_count = 0
        for achievement_data in ACHIEVEMENTS:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
            created_count += 1
            print(f"创建成就: {achievement.name} ({achievement.category})")
        
        # 提交事务
        db.session.commit()
        
        print(f"\n成就初始化完成!")
        print(f"总计创建: {created_count} 个成就")
        
        # 统计各类别数量
        categories = {}
        for achievement in Achievement.query.all():
            categories[achievement.category] = categories.get(achievement.category, 0) + 1
        
        print("\n成就分类统计:")
        for category, count in categories.items():
            print(f"  {category}: {count} 个")
        
        # 统计各等级数量
        tiers = {}
        for achievement in Achievement.query.all():
            tiers[achievement.tier] = tiers.get(achievement.tier, 0) + 1
        
        print("\n成就等级统计:")
        for tier, count in sorted(tiers.items()):
            tier_name = {1: '铜牌', 2: '银牌', 3: '金牌'}.get(tier, f'Tier {tier}')
            print(f"  {tier_name}: {count} 个")


if __name__ == '__main__':
    init_achievements()
