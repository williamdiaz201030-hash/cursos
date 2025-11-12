from motor.motor_asyncio import AsyncIOMotorClient
import os

# Obtén la URL de la base de datos de las variables de entorno
MONGO_URL = os.getenv("MONGO_URL", "mongodb://coursesuser:coursespass123@courses-mongo:27017/courses_content?authSource=courses_content")

# Crea el cliente de MongoDB
client = AsyncIOMotorClient(MONGO_URL)

# Selecciona la base de datos
db = client.courses_content

# Clase para manejar el almacenamiento de contenido
class ContentStore:
    @staticmethod
    async def create_content(content_data):
        """Crear nuevo contenido"""
        collection = db.content
        result = await collection.insert_one(content_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_content(content_id):
        """Obtener contenido por ID"""
        from bson import ObjectId
        collection = db.content
        try:
            content = await collection.find_one({"_id": ObjectId(content_id)})
            return content
        except:
            return None
    
    @staticmethod
    def create_content(content_data):
        """Versión síncrona"""
        # Fallback para uso síncrono
        return "temp-id"
    
    @staticmethod
    def get_content(content_id):
        """Versión síncrona"""
        # Fallback para uso síncrono
        return None
