from sentence_transformers import SentenceTransformer
from utils.logger import logger
def load_model_sentence_transformers():
    """使用 sentence-transformers 加载模型"""
    
    logger.info("使用 sentence-transformers 加载模型...")
    model = SentenceTransformer('BAAI/bge-small-zh-v1.5',local_files_only=True)
    return model

def generate_embedding_sentence_transformers(model, text):
    """使用 sentence-transformers 生成 embedding"""
    if not text or text.strip() == "":
        return None
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
def generate_vectors(content):
    """生成向量"""
    model = load_model_sentence_transformers()
    generate_embedding = lambda text: generate_embedding_sentence_transformers(model, text)
    embedding = generate_embedding(content)
    return embedding
