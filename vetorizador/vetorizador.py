import os
from docx import Document
from pymongo import MongoClient
from transformers import AutoTokenizer, AutoModel
import torch
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definição da string de conexão do MongoDB
os.environ["MONGODB_CONNECTION_STRING"] = "mongodb://localhost:27017/"

# Leitura do documento DOCX
def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Vetorização do texto
def vectorize_text(text):
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.detach().numpy().tolist()

# Conexão com o MongoDB e armazenamento dos vetores
def store_vectors_in_mongodb(vectors, db_name, collection_name):
    try:
        with MongoClient(os.environ["MONGODB_CONNECTION_STRING"]) as client:
            db = client[db_name]
            collection = db[collection_name]
            collection.insert_one({"vectors": vectors})
            logger.info("Vetor armazenado com sucesso no MongoDB.")
    except Exception as e:
        logger.error(f"Erro ao armazenar vetor no MongoDB: {e}")

# Caminho para o arquivo DOCX
file_path = 'data/relatorio_aso.docx'

# Verificação de conexão antes de iniciar o processo
def test_mongodb_connection():
    try:
        with MongoClient(os.environ["MONGODB_CONNECTION_STRING"]) as client:
            # Verifica a listagem de bancos de dados como teste de conexão
            db_list = client.list_database_names()
            logger.info("Conexão com MongoDB bem-sucedida.")
            return True
    except Exception as e:
        logger.error(f"Erro ao conectar ao MongoDB: {e}")
        return False

if test_mongodb_connection():
    # Leitura e vetorização do documento
    try:
        text = read_docx(file_path)
        vectors = vectorize_text(text)
        store_vectors_in_mongodb(vectors, "Marketing", "knowledgement")
    except Exception as e:
        logger.error(f"Erro no processo de vetorização: {e}")
else:
    logger.error("Conexão com MongoDB falhou. Verifique as configurações e tente novamente.")
