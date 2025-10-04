from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
import sys
from sentence_transformers import SentenceTransformer
from models.user import User
from models.ai_data import AISummary

# ============ 配置区域 ============
DATABASE_URL = "postgresql://karl:karl123@localhost:5432/karl"


def load_model_sentence_transformers():
    """使用 sentence-transformers 加载模型"""
    
    print("使用 sentence-transformers 加载模型...")
    model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
    return model

def generate_embedding_sentence_transformers(model, text):
    """使用 sentence-transformers 生成 embedding"""
    if not text or text.strip() == "":
        return None
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
def fill_existing_vectors(batch_size=50):
    """
    填充现有记录的 vector 字段
    
    Args:
        batch_size: 每次提交的记录数，避免一次性提交过多
    """
    # 初始化数据库连接
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    
    model = load_model_sentence_transformers()
    generate_embedding = lambda text: generate_embedding_sentence_transformers(model, text)

    try:
        # 导入模型类
        from models.daily_record import DailyRecord
        
        # 查询所有 vector 为 NULL 但 content 不为 NULL 的记录
        records = session.query(DailyRecord).filter(
            DailyRecord.vector.is_(None),
            DailyRecord.content.isnot(None),
            DailyRecord.content != ''
        ).all()
        
        total_count = len(records)
        print(f"\n找到 {total_count} 条需要生成向量的记录")
        
        if total_count == 0:
            print("没有需要处理的记录！")
            return
        
        # 确认是否继续
        confirm = input(f"\n是否继续为这 {total_count} 条记录生成向量？(y/n): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return
        
        # 批量处理
        success_count = 0
        error_count = 0
        
        print("\n开始生成向量...")
        for i, record in enumerate(tqdm(records, desc="处理进度"), 1):
            try:
                # 生成 embedding
                embedding = generate_embedding(record.content)
                
                if embedding:
                    record.vector = embedding
                    success_count += 1
                else:
                    error_count += 1
                    print(f"\n警告: 记录 ID {record.id} 生成的向量为空")
                
                # 批量提交
                if i % batch_size == 0:
                    session.commit()
                    print(f"\n已提交 {i}/{total_count} 条记录")
                    
            except Exception as e:
                error_count += 1
                print(f"\n错误: 处理记录 ID {record.id} 时出错: {str(e)}")
                continue
        
        # 提交剩余的记录
        session.commit()
        
        # 输出统计信息
        print("\n" + "="*50)
        print("处理完成！")
        print(f"成功: {success_count} 条")
        print(f"失败: {error_count} 条")
        print(f"总计: {total_count} 条")
        print("="*50)
        
    except Exception as e:
        session.rollback()
        print(f"\n发生严重错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()
        engine.dispose()


def verify_vectors():
    """验证向量是否填充成功"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        from models.daily_record import DailyRecord
        
        total = session.query(DailyRecord).filter(
            DailyRecord.content.isnot(None),
            DailyRecord.content != ''
        ).count()
        
        with_vector = session.query(DailyRecord).filter(
            DailyRecord.vector.isnot(None)
        ).count()
        
        without_vector = session.query(DailyRecord).filter(
            DailyRecord.vector.is_(None),
            DailyRecord.content.isnot(None),
            DailyRecord.content != ''
        ).count()
        
        print("\n向量填充情况统计:")
        print(f"有内容的记录总数: {total}")
        print(f"已有向量的记录: {with_vector}")
        print(f"缺少向量的记录: {without_vector}")
        
        if without_vector == 0:
            print("\n✅ 所有记录的向量都已填充完成！")
        else:
            print(f"\n⚠️  还有 {without_vector} 条记录需要填充向量")
            
    finally:
        session.close()
        engine.dispose()
if __name__ == "__main__":
   
    
    # 先验证当前状态
    verify_vectors()
    
    # 执行填充
    print("\n开始填充向量...")
    fill_existing_vectors(batch_size=50)
    
    # 再次验证
    print("\n最终状态:")
    verify_vectors()