from dotenv import load_dotenv
from app import app_factory

# Load environment variables
load_dotenv()

if (__name__ == "__main__"):
  app = app_factory()
  app.run(host="0.0.0.0", port=5000)