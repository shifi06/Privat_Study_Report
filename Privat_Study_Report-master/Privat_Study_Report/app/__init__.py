import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager, UserMixin
from .repository import JsonRepository
from .services import ReportService

# Path database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.json'))

# Init Repo & Service
repo = JsonRepository(db_path)
service = ReportService(repo)
login_manager = LoginManager()

# Model User untuk Flask-Login
class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict.get('id')
        self.nama = user_dict.get('nama')
        self.email = user_dict.get('email')
        self.role = user_dict.get('role')
        self.student_id = user_dict.get('student_id') # Khusus Orang Tua

@login_manager.user_loader
def load_user(user_id):
    user_dict = repo.get_user_by_id(user_id)
    if user_dict:
        return User(user_dict)
    return None

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.login'))

def create_app():
    app = Flask(__name__)
    
    # --- KONFIGURASI SECRET KEY ---
    # Penting: Secret key harus diset SEBELUM inisialisasi login_manager
    app.config['SECRET_KEY'] = 'rahasia-privat-report-super-aman-123' 
    # Opsional: Set session protection
    app.config['SESSION_TYPE'] = 'filesystem' 

    login_manager.init_app(app)
    # Opsional: Set login view untuk redirect otomatis jika user belum login mengakses halaman terproteksi
    login_manager.login_view = 'auth.login' 

    with app.app_context():
        from . import auth, routes
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(routes.main_bp)

    return app