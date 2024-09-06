from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
