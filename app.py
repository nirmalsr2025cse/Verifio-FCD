from flask import Flask
from utils.config import appConf
from utils.oauth import init_oauth
from auth.routes import auth
from auth.oauth import oauth_bp
from password.routes import password
from dashboard.routes import dashboard

app = Flask(__name__)
app.secret_key = appConf["FLASK_SECRET"]
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

init_oauth(app)

app.register_blueprint(auth)
app.register_blueprint(oauth_bp)
app.register_blueprint(password)
app.register_blueprint(dashboard)

if __name__ == "__main__":
    app.run(host="localhost",port=5000,debug=True)