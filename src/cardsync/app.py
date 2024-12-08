import os
from dotenv import load_dotenv
from cardmanager import create_app

load_dotenv()
config_name = os.getenv("FLASK_CONFIG", "default")
app = create_app(config_name)

if __name__ == "__main__":
    app.run(debug=True)
