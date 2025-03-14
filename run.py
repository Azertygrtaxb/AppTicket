from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from app.routes.user import User
from app.routes.base import base_route

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = 'appticket_secret_key'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "base_route.login"

@login_manager.user_loader
def load_user(username):
    return User(username)

app.register_blueprint(base_route)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
