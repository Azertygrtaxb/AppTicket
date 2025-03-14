from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

class User(UserMixin):
    def __init__(self, username):
        self.id = username