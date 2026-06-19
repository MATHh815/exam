"""
生成示例题目数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question
from app.models.knowledge_point import KnowledgePoint
import random

def generate_all_questions():
    """生成所有科目的题目"""
    all_questions = []
    
    # ==================== Python题目 ====================
    python_questions = [
        {
            'content': '在Python中，以下哪个关键字用于定义函数？',
            'options': ['A. function', 'B. def', 'C. func', 'D. define'],
            'answer': 'B',
            'analysis': 'Python使用def关键字来定义函数。',
            'difficulty': 'easy',
            'knowledge_point': '函数定义',
            'subject': 'Python',
            'chapter': '第3章 函数'
        },
        {
            'content': '以下哪个不是Python的数据类型？',
            'options': ['A. int', 'B. float', 'C. char', 'D. str'],
            'answer': 'C',
            'analysis': 'Python没有char类型，字符串使用str类型。',
            'difficulty': 'easy',
            'knowledge_point': '变量与数据类型',
            'subject': 'Python',
            'chapter': '第1章 基础'
        },
        {
            'content': 'Python中如何创建一个空列表？',
            'options': ['A. list()', 'B. []', 'C. {}', 'D. A和B都可以'],
            'answer': 'D',
            'analysis': 'Python中可以使用[]或list()来创建空列表。',
            'difficulty': 'easy',
            'knowledge_point': '列表与元组',
            'subject': 'Python',
            'chapter': '第2章 数据结构'
        },
        {
            'content': '以下哪个方法可以向列表末尾添加元素？',
            'options': ['A. add()', 'B. append()', 'C. insert()', 'D. push()'],
            'answer': 'B',
            'analysis': 'append()方法用于在列表末尾添加元素。',
            'difficulty': 'easy',
            'knowledge_point': '列表与元组',
            'subject': 'Python',
            'chapter': '第2章 数据结构'
        },
        {
            'content': 'Python中的字典使用什么符号表示？',
            'options': ['A. []', 'B. ()', 'C. {}', 'D. <>'],
            'answer': 'C',
            'analysis': 'Python字典使用大括号{}表示。',
            'difficulty': 'easy',
            'knowledge_point': '字典与集合',
            'subject': 'Python',
            'chapter': '第2章 数据结构'
        },
        {
            'content': '以下哪个是Python中的循环语句？',
            'options': ['A. for', 'B. while', 'C. loop', 'D. A和B'],
            'answer': 'D',
            'analysis': 'Python支持for和while两种循环语句。',
            'difficulty': 'easy',
            'knowledge_point': '循环结构',
            'subject': 'Python',
            'chapter': '第3章 控制流'
        },
        {
            'content': 'Python中如何定义一个类？',
            'options': ['A. class MyClass:', 'B. def MyClass:', 'C. new MyClass:', 'D. create MyClass:'],
            'answer': 'A',
            'analysis': 'Python使用class关键字定义类。',
            'difficulty': 'medium',
            'knowledge_point': '面向对象',
            'subject': 'Python',
            'chapter': '第5章 面向对象'
        },
        {
            'content': '以下哪个是Python的装饰器语法？',
            'options': ['A. #decorator', 'B. @decorator', 'C. &decorator', 'D. *decorator'],
            'answer': 'B',
            'analysis': 'Python使用@符号表示装饰器。',
            'difficulty': 'medium',
            'knowledge_point': '装饰器',
            'subject': 'Python',
            'chapter': '第6章 高级特性'
        },
        {
            'content': 'Python中的lambda表达式用于创建什么？',
            'options': ['A. 匿名函数', 'B. 类', 'C. 模块', 'D. 包'],
            'answer': 'A',
            'analysis': 'lambda表达式用于创建匿名函数。',
            'difficulty': 'medium',
            'knowledge_point': '函数定义',
            'subject': 'Python',
            'chapter': '第3章 函数'
        },
        {
            'content': '以下哪个方法可以将字符串转换为整数？',
            'options': ['A. int()', 'B. str()', 'C. float()', 'D. convert()'],
            'answer': 'A',
            'analysis': 'int()函数用于将字符串转换为整数。',
            'difficulty': 'easy',
            'knowledge_point': '变量与数据类型',
            'subject': 'Python',
            'chapter': '第1章 基础'
        },
        {
            'content': 'Python中的生成器使用什么关键字？',
            'options': ['A. return', 'B. yield', 'C. generate', 'D. create'],
            'answer': 'B',
            'analysis': 'yield关键字用于创建生成器。',
            'difficulty': 'hard',
            'knowledge_point': '迭代器与生成器',
            'subject': 'Python',
            'chapter': '第6章 高级特性'
        },
        {
            'content': '以下哪个是Python的异常处理语句？',
            'options': ['A. try-catch', 'B. try-except', 'C. catch-throw', 'D. error-handle'],
            'answer': 'B',
            'analysis': 'Python使用try-except进行异常处理。',
            'difficulty': 'medium',
            'knowledge_point': '异常处理',
            'subject': 'Python',
            'chapter': '第4章 异常处理'
        },
        {
            'content': 'Python中如何导入模块？',
            'options': ['A. include', 'B. import', 'C. require', 'D. using'],
            'answer': 'B',
            'analysis': 'Python使用import关键字导入模块。',
            'difficulty': 'easy',
            'knowledge_point': '模块与包',
            'subject': 'Python',
            'chapter': '第7章 模块'
        },
        {
            'content': '以下哪个是Python的文件打开模式？',
            'options': ['A. r', 'B. w', 'C. a', 'D. 以上都是'],
            'answer': 'D',
            'analysis': 'Python支持r(读)、w(写)、a(追加)等多种文件打开模式。',
            'difficulty': 'easy',
            'knowledge_point': '文件操作',
            'subject': 'Python',
            'chapter': '第8章 文件IO'
        },
        {
            'content': 'Python中的列表推导式语法是什么？',
            'options': ['A. [x for x in range(10)]', 'B. {x for x in range(10)}', 'C. (x for x in range(10))', 'D. list(x for x in range(10))'],
            'answer': 'A',
            'analysis': '列表推导式使用方括号[]包围。',
            'difficulty': 'medium',
            'knowledge_point': '推导式',
            'subject': 'Python',
            'chapter': '第6章 高级特性'
        },
    ]
    
    # 数据结构题目
    data_structure = [
        {
            'content': '栈的特点是什么？',
            'options': ['A. 先进先出', 'B. 先进后出', 'C. 随机访问', 'D. 顺序访问'],
            'answer': 'B',
            'analysis': '栈是一种后进先出(LIFO)的数据结构。',
            'difficulty': 'easy',
            'knowledge_point': '栈',
            'subject': '数据结构',
            'chapter': '第3章 栈和队列'
        },
        {
            'content': '队列的特点是什么？',
            'options': ['A. 先进先出', 'B. 先进后出', 'C. 随机访问', 'D. 双向访问'],
            'answer': 'A',
            'analysis': '队列是一种先进先出(FIFO)的数据结构。',
            'difficulty': 'easy',
            'knowledge_point': '队列',
            'subject': '数据结构',
            'chapter': '第3章 栈和队列'
        },
        {
            'content': '链表相比数组的优势是什么？',
            'options': ['A. 随机访问快', 'B. 插入删除快', 'C. 内存连续', 'D. 查找快'],
            'answer': 'B',
            'analysis': '链表的插入和删除操作时间复杂度为O(1)，比数组快。',
            'difficulty': 'medium',
            'knowledge_point': '链表',
            'subject': '数据结构',
            'chapter': '第2章 线性表'
        },
        {
            'content': '二叉树的遍历方式有哪些？',
            'options': ['A. 前序、中序、后序', 'B. 深度优先、广度优先', 'C. 顺序、逆序', 'D. A和B都对'],
            'answer': 'D',
            'analysis': '二叉树可以按前中后序遍历，也可以按深度或广度优先遍历。',
            'difficulty': 'medium',
            'knowledge_point': '二叉树',
            'subject': '数据结构',
            'chapter': '第5章 树'
        },
        {
            'content': '哈希表的平均查找时间复杂度是多少？',
            'options': ['A. O(1)', 'B. O(log n)', 'C. O(n)', 'D. O(n²)'],
            'answer': 'A',
            'analysis': '哈希表通过哈希函数直接定位，平均时间复杂度为O(1)。',
            'difficulty': 'medium',
            'knowledge_point': '哈希表',
            'subject': '数据结构',
            'chapter': '第7章 查找'
        },
        {
            'content': '完全二叉树的定义是什么？',
            'options': ['A. 每个节点都有两个子节点', 'B. 除最后一层外都是满的，最后一层从左到右连续', 'C. 所有叶子节点在同一层', 'D. 左右子树高度相等'],
            'answer': 'B',
            'analysis': '完全二叉树除最后一层外都是满的，最后一层节点从左到右连续排列。',
            'difficulty': 'medium',
            'knowledge_point': '二叉树',
            'subject': '数据结构',
            'chapter': '第5章 树'
        },
        {
            'content': '图的存储方式有哪些？',
            'options': ['A. 邻接矩阵', 'B. 邻接表', 'C. 十字链表', 'D. 以上都是'],
            'answer': 'D',
            'analysis': '图可以用邻接矩阵、邻接表、十字链表等多种方式存储。',
            'difficulty': 'medium',
            'knowledge_point': '图',
            'subject': '数据结构',
            'chapter': '第6章 图'
        },
        {
            'content': '堆排序的时间复杂度是多少？',
            'options': ['A. O(n)', 'B. O(n log n)', 'C. O(n²)', 'D. O(log n)'],
            'answer': 'B',
            'analysis': '堆排序的时间复杂度为O(n log n)。',
            'difficulty': 'medium',
            'knowledge_point': '排序算法',
            'subject': '数据结构',
            'chapter': '第8章 排序'
        },
    ]
    
    # 算法题目
    algorithm = [
        {
            'content': '二分查找的前提条件是什么？',
            'options': ['A. 数组有序', 'B. 数组无序', 'C. 数组长度为偶数', 'D. 数组元素唯一'],
            'answer': 'A',
            'analysis': '二分查找要求数组必须是有序的。',
            'difficulty': 'easy',
            'knowledge_point': '查找算法',
            'subject': '算法',
            'chapter': '第2章 查找'
        },
        {
            'content': '快速排序的平均时间复杂度是多少？',
            'options': ['A. O(n)', 'B. O(n log n)', 'C. O(n²)', 'D. O(log n)'],
            'answer': 'B',
            'analysis': '快速排序的平均时间复杂度为O(n log n)。',
            'difficulty': 'medium',
            'knowledge_point': '排序算法',
            'subject': '算法',
            'chapter': '第3章 排序'
        },
        {
            'content': '动态规划的核心思想是什么？',
            'options': ['A. 分治', 'B. 贪心', 'C. 记忆化搜索', 'D. 回溯'],
            'answer': 'C',
            'analysis': '动态规划通过记忆化搜索避免重复计算。',
            'difficulty': 'hard',
            'knowledge_point': '动态规划',
            'subject': '算法',
            'chapter': '第5章 动态规划'
        },
        {
            'content': '贪心算法的特点是什么？',
            'options': ['A. 每步选择当前最优', 'B. 考虑全局最优', 'C. 需要回溯', 'D. 时间复杂度高'],
            'answer': 'A',
            'analysis': '贪心算法每步都选择当前最优解，不考虑全局。',
            'difficulty': 'medium',
            'knowledge_point': '贪心算法',
            'subject': '算法',
            'chapter': '第4章 贪心'
        },
        {
            'content': 'DFS和BFS的区别是什么？',
            'options': ['A. DFS用栈，BFS用队列', 'B. DFS用队列，BFS用栈', 'C. 都用栈', 'D. 都用队列'],
            'answer': 'A',
            'analysis': 'DFS使用栈(递归)，BFS使用队列。',
            'difficulty': 'medium',
            'knowledge_point': '图遍历',
            'subject': '算法',
            'chapter': '第6章 图算法'
        },
        {
            'content': '最短路径算法Dijkstra适用于什么图？',
            'options': ['A. 有向图', 'B. 无向图', 'C. 无负权边的图', 'D. 任意图'],
            'answer': 'C',
            'analysis': 'Dijkstra算法不能处理负权边。',
            'difficulty': 'hard',
            'knowledge_point': '最短路径',
            'subject': '算法',
            'chapter': '第6章 图算法'
        },
    ]
    
    # ==================== Java题目 ====================
    java_questions = [
        {
            'content': 'Java中的main方法签名是什么？',
            'options': ['A. public static void main(String[] args)', 'B. public void main(String[] args)', 'C. static void main(String[] args)', 'D. void main(String[] args)'],
            'answer': 'A',
            'analysis': 'Java的main方法必须是public static void，参数是String数组。',
            'difficulty': 'easy',
            'knowledge_point': 'Java基础',
            'subject': 'Java',
            'chapter': '第1章 Java入门'
        },
        {
            'content': 'Java中的访问修饰符有哪些？',
            'options': ['A. public, private', 'B. public, private, protected', 'C. public, private, protected, default', 'D. public, private, protected, package'],
            'answer': 'C',
            'analysis': 'Java有四种访问修饰符：public、private、protected和默认(default)。',
            'difficulty': 'easy',
            'knowledge_point': '访问控制',
            'subject': 'Java',
            'chapter': '第2章 面向对象'
        },
        {
            'content': 'Java中的接口可以包含什么？',
            'options': ['A. 抽象方法', 'B. 默认方法', 'C. 静态方法', 'D. 以上都可以'],
            'answer': 'D',
            'analysis': 'Java 8之后，接口可以包含抽象方法、默认方法和静态方法。',
            'difficulty': 'medium',
            'knowledge_point': '接口',
            'subject': 'Java',
            'chapter': '第3章 接口与抽象类'
        },
        {
            'content': 'Java中的异常分为哪两类？',
            'options': ['A. Error和Exception', 'B. RuntimeException和CheckedException', 'C. Checked和Unchecked', 'D. B和C都对'],
            'answer': 'D',
            'analysis': 'Java异常分为RuntimeException(运行时异常)和CheckedException(检查异常)，也称为Checked和Unchecked异常。',
            'difficulty': 'medium',
            'knowledge_point': '异常处理',
            'subject': 'Java',
            'chapter': '第4章 异常处理'
        },
        {
            'content': 'Java中的集合框架主要接口有哪些？',
            'options': ['A. List, Set, Map', 'B. Collection, Map', 'C. ArrayList, HashMap', 'D. Vector, Hashtable'],
            'answer': 'B',
            'analysis': 'Java集合框架的主要接口是Collection和Map。',
            'difficulty': 'medium',
            'knowledge_point': '集合框架',
            'subject': 'Java',
            'chapter': '第5章 集合'
        },
        {
            'content': 'Java中的线程创建方式有哪些？',
            'options': ['A. 继承Thread类', 'B. 实现Runnable接口', 'C. 实现Callable接口', 'D. 以上都是'],
            'answer': 'D',
            'analysis': 'Java可以通过继承Thread、实现Runnable或Callable接口来创建线程。',
            'difficulty': 'medium',
            'knowledge_point': '多线程',
            'subject': 'Java',
            'chapter': '第6章 并发编程'
        },
        {
            'content': 'Java中的synchronized关键字用于什么？',
            'options': ['A. 线程同步', 'B. 异常处理', 'C. 内存管理', 'D. 类加载'],
            'answer': 'A',
            'analysis': 'synchronized用于实现线程同步，保证线程安全。',
            'difficulty': 'medium',
            'knowledge_point': '多线程',
            'subject': 'Java',
            'chapter': '第6章 并发编程'
        },
        {
            'content': 'Java中的泛型有什么作用？',
            'options': ['A. 类型安全', 'B. 代码复用', 'C. 避免类型转换', 'D. 以上都是'],
            'answer': 'D',
            'analysis': '泛型提供类型安全、代码复用和避免类型转换的好处。',
            'difficulty': 'medium',
            'knowledge_point': '泛型',
            'subject': 'Java',
            'chapter': '第7章 泛型'
        },
    ]
    
    # ==================== C++题目 ====================
    cpp_questions = [
        {
            'content': 'C++中的指针和引用的区别是什么？',
            'options': ['A. 指针可以为空，引用不能', 'B. 指针可以改变指向，引用不能', 'C. 指针需要解引用，引用不需要', 'D. 以上都对'],
            'answer': 'D',
            'analysis': '指针和引用的主要区别包括：指针可以为空、可以改变指向、需要解引用。',
            'difficulty': 'medium',
            'knowledge_point': '指针与引用',
            'subject': 'C++',
            'chapter': '第2章 指针'
        },
        {
            'content': 'C++中的虚函数用于实现什么？',
            'options': ['A. 多态', 'B. 封装', 'C. 继承', 'D. 重载'],
            'answer': 'A',
            'analysis': '虚函数用于实现运行时多态。',
            'difficulty': 'medium',
            'knowledge_point': '多态',
            'subject': 'C++',
            'chapter': '第4章 面向对象'
        },
        {
            'content': 'C++中的构造函数可以是虚函数吗？',
            'options': ['A. 可以', 'B. 不可以', 'C. 有时可以', 'D. 取决于编译器'],
            'answer': 'B',
            'analysis': '构造函数不能是虚函数，因为对象还未创建完成。',
            'difficulty': 'hard',
            'knowledge_point': '构造函数',
            'subject': 'C++',
            'chapter': '第4章 面向对象'
        },
        {
            'content': 'C++中的智能指针有哪些？',
            'options': ['A. unique_ptr', 'B. shared_ptr', 'C. weak_ptr', 'D. 以上都是'],
            'answer': 'D',
            'analysis': 'C++11引入了unique_ptr、shared_ptr和weak_ptr三种智能指针。',
            'difficulty': 'medium',
            'knowledge_point': '智能指针',
            'subject': 'C++',
            'chapter': '第5章 现代C++'
        },
        {
            'content': 'C++中的STL包含哪些组件？',
            'options': ['A. 容器', 'B. 算法', 'C. 迭代器', 'D. 以上都是'],
            'answer': 'D',
            'analysis': 'STL包含容器、算法、迭代器等组件。',
            'difficulty': 'easy',
            'knowledge_point': 'STL',
            'subject': 'C++',
            'chapter': '第6章 STL'
        },
    ]
    
    # ==================== 数据库题目 ====================
    database_questions = [
        {
            'content': 'SQL中的SELECT语句用于什么？',
            'options': ['A. 查询数据', 'B. 插入数据', 'C. 更新数据', 'D. 删除数据'],
            'answer': 'A',
            'analysis': 'SELECT语句用于从数据库中查询数据。',
            'difficulty': 'easy',
            'knowledge_point': 'SQL基础',
            'subject': '数据库',
            'chapter': '第1章 SQL基础'
        },
        {
            'content': '数据库的ACID特性是什么？',
            'options': ['A. 原子性、一致性、隔离性、持久性', 'B. 可用性、一致性、隔离性、持久性', 'C. 原子性、并发性、隔离性、持久性', 'D. 原子性、一致性、完整性、持久性'],
            'answer': 'A',
            'analysis': 'ACID是原子性(Atomicity)、一致性(Consistency)、隔离性(Isolation)、持久性(Durability)的缩写。',
            'difficulty': 'medium',
            'knowledge_point': '事务',
            'subject': '数据库',
            'chapter': '第3章 事务'
        },
        {
            'content': 'SQL中的JOIN有哪些类型？',
            'options': ['A. INNER JOIN', 'B. LEFT JOIN', 'C. RIGHT JOIN', 'D. 以上都是'],
            'answer': 'D',
            'analysis': 'SQL支持INNER JOIN、LEFT JOIN、RIGHT JOIN等多种连接类型。',
            'difficulty': 'medium',
            'knowledge_point': '连接查询',
            'subject': '数据库',
            'chapter': '第2章 查询'
        },
        {
            'content': '数据库索引的作用是什么？',
            'options': ['A. 加快查询速度', 'B. 保证数据唯一性', 'C. 减少存储空间', 'D. A和B'],
            'answer': 'D',
            'analysis': '索引可以加快查询速度，唯一索引还可以保证数据唯一性。',
            'difficulty': 'easy',
            'knowledge_point': '索引',
            'subject': '数据库',
            'chapter': '第4章 索引'
        },
        {
            'content': '数据库的范式有哪些？',
            'options': ['A. 1NF, 2NF, 3NF', 'B. BCNF, 4NF, 5NF', 'C. A和B都对', 'D. 只有A对'],
            'answer': 'C',
            'analysis': '数据库范式包括1NF、2NF、3NF、BCNF、4NF、5NF等。',
            'difficulty': 'medium',
            'knowledge_point': '范式',
            'subject': '数据库',
            'chapter': '第5章 数据库设计'
        },
        {
            'content': 'NoSQL数据库的特点是什么？',
            'options': ['A. 不使用SQL', 'B. 非关系型', 'C. 高可扩展性', 'D. 以上都是'],
            'answer': 'D',
            'analysis': 'NoSQL数据库的特点包括不使用SQL、非关系型、高可扩展性等。',
            'difficulty': 'medium',
            'knowledge_point': 'NoSQL',
            'subject': '数据库',
            'chapter': '第7章 NoSQL'
        },
    ]
    
    # ==================== 计算机网络题目 ====================
    network_questions = [
        {
            'content': 'OSI模型有几层？',
            'options': ['A. 5层', 'B. 6层', 'C. 7层', 'D. 8层'],
            'answer': 'C',
            'analysis': 'OSI模型有7层：物理层、数据链路层、网络层、传输层、会话层、表示层、应用层。',
            'difficulty': 'easy',
            'knowledge_point': 'OSI模型',
            'subject': '计算机网络',
            'chapter': '第1章 网络基础'
        },
        {
            'content': 'TCP和UDP的区别是什么？',
            'options': ['A. TCP可靠，UDP不可靠', 'B. TCP面向连接，UDP无连接', 'C. TCP慢，UDP快', 'D. 以上都对'],
            'answer': 'D',
            'analysis': 'TCP是可靠的、面向连接的协议，速度较慢；UDP是不可靠的、无连接的协议，速度较快。',
            'difficulty': 'medium',
            'knowledge_point': '传输层协议',
            'subject': '计算机网络',
            'chapter': '第4章 传输层'
        },
        {
            'content': 'HTTP协议默认端口是多少？',
            'options': ['A. 80', 'B. 443', 'C. 8080', 'D. 3306'],
            'answer': 'A',
            'analysis': 'HTTP协议默认使用80端口，HTTPS使用443端口。',
            'difficulty': 'easy',
            'knowledge_point': 'HTTP协议',
            'subject': '计算机网络',
            'chapter': '第7章 应用层'
        },
        {
            'content': 'IP地址分为几类？',
            'options': ['A. 3类', 'B. 4类', 'C. 5类', 'D. 6类'],
            'answer': 'C',
            'analysis': 'IP地址分为A、B、C、D、E五类。',
            'difficulty': 'medium',
            'knowledge_point': 'IP地址',
            'subject': '计算机网络',
            'chapter': '第3章 网络层'
        },
        {
            'content': 'DNS的作用是什么？',
            'options': ['A. 域名解析', 'B. 路由选择', 'C. 数据加密', 'D. 流量控制'],
            'answer': 'A',
            'analysis': 'DNS(Domain Name System)用于将域名解析为IP地址。',
            'difficulty': 'easy',
            'knowledge_point': 'DNS',
            'subject': '计算机网络',
            'chapter': '第7章 应用层'
        },
        {
            'content': 'HTTP状态码200表示什么？',
            'options': ['A. 成功', 'B. 重定向', 'C. 客户端错误', 'D. 服务器错误'],
            'answer': 'A',
            'analysis': 'HTTP状态码200表示请求成功。',
            'difficulty': 'easy',
            'knowledge_point': 'HTTP协议',
            'subject': '计算机网络',
            'chapter': '第7章 应用层'
        },
    ]
    
    # ==================== 操作系统题目 ====================
    os_questions = [
        {
            'content': '操作系统的主要功能是什么？',
            'options': ['A. 进程管理', 'B. 内存管理', 'C. 文件管理', 'D. 以上都是'],
            'answer': 'D',
            'analysis': '操作系统的主要功能包括进程管理、内存管理、文件管理、设备管理等。',
            'difficulty': 'easy',
            'knowledge_point': '操作系统概述',
            'subject': '操作系统',
            'chapter': '第1章 概述'
        },
        {
            'content': '进程和线程的区别是什么？',
            'options': ['A. 进程是资源分配单位，线程是调度单位', 'B. 进程有独立地址空间，线程共享地址空间', 'C. 进程切换开销大，线程切换开销小', 'D. 以上都对'],
            'answer': 'D',
            'analysis': '进程是资源分配单位，线程是调度单位；进程有独立地址空间，线程共享；进程切换开销大于线程。',
            'difficulty': 'medium',
            'knowledge_point': '进程与线程',
            'subject': '操作系统',
            'chapter': '第2章 进程管理'
        },
        {
            'content': '死锁的四个必要条件是什么？',
            'options': ['A. 互斥、占有且等待、不可抢占、循环等待', 'B. 互斥、等待、抢占、循环', 'C. 占有、等待、不可抢占、死循环', 'D. 互斥、占有、抢占、等待'],
            'answer': 'A',
            'analysis': '死锁的四个必要条件是：互斥条件、占有且等待、不可抢占、循环等待。',
            'difficulty': 'hard',
            'knowledge_point': '死锁',
            'subject': '操作系统',
            'chapter': '第2章 进程管理'
        },
        {
            'content': '页面置换算法有哪些？',
            'options': ['A. FIFO', 'B. LRU', 'C. LFU', 'D. 以上都是'],
            'answer': 'D',
            'analysis': '常见的页面置换算法包括FIFO、LRU、LFU等。',
            'difficulty': 'medium',
            'knowledge_point': '内存管理',
            'subject': '操作系统',
            'chapter': '第3章 内存管理'
        },
        {
            'content': '文件系统的作用是什么？',
            'options': ['A. 管理文件', 'B. 提供文件访问接口', 'C. 保护文件安全', 'D. 以上都是'],
            'answer': 'D',
            'analysis': '文件系统负责管理文件、提供访问接口、保护文件安全等。',
            'difficulty': 'easy',
            'knowledge_point': '文件系统',
            'subject': '操作系统',
            'chapter': '第4章 文件管理'
        },
    ]
    
    # 合并所有题目
    all_questions = (
        python_questions + 
        java_questions + 
        cpp_questions + 
        database_questions + 
        network_questions + 
        os_questions +
        data_structure + 
        algorithm
    )
    
    return all_questions

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("开始生成题目数据")
        print("=" * 60)
        
        try:
            # 获取知识点映射
            knowledge_points = KnowledgePoint.query.all()
            kp_dict = {kp.name: kp for kp in knowledge_points}
            
            # 生成题目
            questions_data = generate_all_questions()
            
            created_count = 0
            skipped_count = 0
            
            for q_data in questions_data:
                # 检查题目是否已存在
                existing = Question.query.filter_by(content=q_data['content']).first()
                if existing:
                    skipped_count += 1
                    continue
                
                # 获取知识点
                kp_name = q_data.pop('knowledge_point')
                kp = kp_dict.get(kp_name)
                
                if not kp:
                    # 如果知识点不存在，创建一个
                    kp = KnowledgePoint(
                        name=kp_name,
                        subject=q_data['subject'],
                        chapter=q_data['chapter'],
                        difficulty=q_data['difficulty']
                    )
                    db.session.add(kp)
                    db.session.flush()
                    kp_dict[kp_name] = kp
                
                # 创建题目
                question = Question(
                    content=q_data['content'],
                    options=q_data['options'],
                    answer=q_data['answer'],
                    analysis=q_data['analysis'],
                    difficulty=q_data['difficulty'],
                    subject=q_data['subject'],
                    chapter=q_data['chapter'],
                    knowledge_point_id=kp.id
                )
                
                db.session.add(question)
                created_count += 1
            
            db.session.commit()
            
            print(f"\n✓ 题目生成完成")
            print(f"  - 创建题目: {created_count} 道")
            print(f"  - 跳过题目: {skipped_count} 道")
            
            # 统计信息
            total_questions = Question.query.count()
            print(f"  - 总题目数: {total_questions} 道")
            
            # 按科目统计
            subjects = db.session.query(
                Question.subject,
                db.func.count(Question.id)
            ).group_by(Question.subject).all()
            
            print(f"\n按科目统计:")
            for subject, count in subjects:
                print(f"  - {subject}: {count} 道")
            
            # 按难度统计
            difficulties = db.session.query(
                Question.difficulty,
                db.func.count(Question.id)
            ).group_by(Question.difficulty).all()
            
            print(f"\n按难度统计:")
            for difficulty, count in difficulties:
                print(f"  - {difficulty}: {count} 道")
            
            print("\n" + "=" * 60)
            print("题目生成完成！")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n✗ 生成失败: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
