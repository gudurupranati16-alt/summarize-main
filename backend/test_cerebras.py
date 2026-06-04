from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
import os

load_dotenv()

client = Cerebras(
    api_key=os.getenv("CEREBRAS_API_KEY")
)

try:
    models = client.models.list()
    print(models)
except Exception as e:
    print("ERROR:", e)
    