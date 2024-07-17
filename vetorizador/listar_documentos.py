import os
from pymongo import MongoClient
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definição da string de conexão do MongoDB
os.environ["MONGODB_CONNECTION_STRING"] = os.getenv("MONGODB_CONNECTION_STRING")

# Função para listar todos os documentos em uma coleção
def list_all_documents(db_name, collection_name):
    try:
        with MongoClient(os.environ["MONGODB_CONNECTION_STRING"]) as client:
            db = client[db_name]
            collection = db[collection_name]
            documents = collection.find()
            for doc in documents:
                logger.info(doc)
    except Exception as e:
        logger.error(f"Erro ao listar documentos do MongoDB: {e}")

# Listar todos os documentos na coleção 'knowledgement' do banco de dados 'Marketing'
list_all_documents("Marketing", "knowledgement")
