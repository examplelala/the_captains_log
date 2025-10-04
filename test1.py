"""
简单的向量检索实现
用户输入文字 -> 转成向量 -> 和数据库中的 content 向量对比 -> 返回最相似的记录
"""

from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.user import User
from models.ai_data import AISummary

# ============ 配置区域 ============
DATABASE_URL = "postgresql://karl:karl123@localhost:5432/karl"
# ==============================

# 全局加载模型（只加载一次，提高效率）
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

# 数据库连接
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def search_by_text(user_input: str, top_k: int = 5, user_id: int = None):
    """
    根据用户输入的文字进行向量检索
    
    Args:
        user_input: 用户输入的文字（不需要预处理，直接传入即可）
        top_k: 返回前几条最相似的结果
        user_id: 可选，只搜索该用户的记录
    
    Returns:
        最相似的记录列表
    """
    
    # 步骤1: 把用户输入转成向量（不需要任何预处理）
    print(f"正在将输入文字转换为向量...")
    query_vector = model.encode(user_input, normalize_embeddings=True)
    
    # 步骤2: 构建 SQL 查询，使用 pgvector 的余弦距离
    # <=> 是余弦距离运算符，值越小越相似
    # 1 - 余弦距离 = 余弦相似度（值越大越相似）
    
    session = SessionLocal()
    
    try:
        sql = """
            SELECT 
                id,
                user_id,
                record_date,
                content,
                mood_score,
                reflections,
                (1 - (vector <=> :query_vector)) as similarity
            FROM daily_records
            WHERE vector IS NOT NULL
        """
        
        # 如果指定了用户ID，添加过滤条件
        if user_id is not None:
            sql += " AND user_id = :user_id"
        
        # 按相似度排序，取前 top_k 条
        sql += """
            ORDER BY vector <=> :query_vector
            LIMIT :top_k
        """
        
        # 执行查询
        # 关键：向量需要转成字符串格式 '[0.1, 0.2, ...]'
        vector_str = '[' + ','.join(map(str, query_vector.tolist())) + ']'
        
        params = {
            'query_vector': vector_str,  # 字符串格式的向量
            'top_k': top_k
        }
        
        if user_id is not None:
            params['user_id'] = user_id
        
        result = session.execute(text(sql), params)
        
        # 步骤3: 获取结果
        records = []
        for row in result:
            records.append({
                'id': row.id,
                'user_id': row.user_id,
                'date': row.record_date,
                'content': row.content,
                'mood_score': row.mood_score,
                'reflections': row.reflections,
                'similarity': round(float(row.similarity), 4)  # 相似度分数（0-1，越接近1越相似）
            })
        
        return records
        
    finally:
        session.close()


def demo():
    """演示如何使用"""
    
    print("="*60)
    print("向量检索演示")
    print("="*60)
    
    # 例子1: 搜索关于工作的记录
    user_input = "今天工作压力很大"
    print(f"\n查询: {user_input}")
    print("-"*60)
    
    results = search_by_text(user_input, top_k=3)
    
    if not results:
        print("没有找到相关记录")
    else:
        for i, record in enumerate(results, 1):
            print(f"\n结果 {i} (相似度: {record['similarity']})")
            print(f"日期: {record['date']}")
            print(f"内容: {record['content'][:100]}...")
            if record['mood_score']:
                print(f"心情: {record['mood_score']}/10")
    
    print("\n" + "="*60)
    
    # 例子2: 搜索关于心情的记录
    user_input = "心情不好想哭"
    print(f"\n查询: {user_input}")
    print("-"*60)
    
    results = search_by_text(user_input, top_k=3)
    
    for i, record in enumerate(results, 1):
        print(f"\n结果 {i} (相似度: {record['similarity']})")
        print(f"日期: {record['date']}")
        print(f"内容: {record['content'][:100]}...")


def interactive_search():
    """交互式搜索"""
    print("\n🔍 向量检索系统")
    print("输入 'quit' 或 'exit' 退出\n")
    
    while True:
        user_input = input("请输入要搜索的内容: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("再见！")
            break
        
        if not user_input:
            print("输入不能为空，请重新输入\n")
            continue
        
        print(f"\n正在搜索 '{user_input}'...\n")
        
        results = search_by_text(user_input, top_k=5)
        
        if not results:
            print("❌ 没有找到相关记录\n")
        else:
            print(f"✅ 找到 {len(results)} 条相关记录:\n")
            for i, record in enumerate(results, 1):
                print(f"{'─'*50}")
                print(f"📝 结果 {i} | 相似度: {record['similarity']*100:.1f}%")
                print(f"📅 日期: {record['date']}")
                if record['mood_score']:
                    print(f"😊 心情: {record['mood_score']}/10")
                print(f"💭 内容: {record['content'][:150]}...")
                if record['reflections']:
                    print(f"🤔 反思: {record['reflections'][:100]}...")
                print()
        
        print()


# ============ 使用 ORM 的方式（可选） ============
def search_by_text_orm(user_input: str, top_k: int = 5, user_id: int = None):
    """
    使用 SQLAlchemy ORM 的方式进行检索
    """
    from models.daily_record import DailyRecord
    
    # 转换为向量（字符串格式）
    query_vector_array = model.encode(user_input, normalize_embeddings=True).tolist()
    query_vector = '[' + ','.join(map(str, query_vector_array)) + ']'
    
    session = SessionLocal()
    try:
        # 使用原生 SQL（ORM 在这里不太好用）
        sql = text("""
            SELECT 
                id, user_id, record_date, content, mood_score, reflections,
                (1 - (vector <=> :query_vector::vector)) as similarity
            FROM daily_records
            WHERE vector IS NOT NULL
            """ + (" AND user_id = :user_id" if user_id else "") + """
            ORDER BY vector <=> :query_vector::vector
            LIMIT :top_k
        """)
        
        params = {'query_vector': query_vector, 'top_k': top_k}
        if user_id:
            params['user_id'] = user_id
        
        result = session.execute(sql, params)
        
        # 格式化返回
        return [
            {
                'id': row.id,
                'user_id': row.user_id,
                'date': row.record_date,
                'content': row.content,
                'mood_score': row.mood_score,
                'reflections': row.reflections,
                'similarity': round(float(row.similarity), 4)
            }
            for row in result
        ]
        
    finally:
        session.close()


if __name__ == "__main__":
    # 运行演示
    demo()
    