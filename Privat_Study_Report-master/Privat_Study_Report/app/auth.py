from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import repo, User, service 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_data = repo.get_user_by_email(email)
        
        if user_data and user_data['password'] == password:
            user = User(user_data)
            login_user(user)
            
            if user.role == 'admin':
                return redirect(url_for('main.dashboard_admin'))
            elif user.role == 'guru':
                return redirect(url_for('main.dashboard_guru'))
            elif user.role == 'orangtua':
                return redirect(url_for('main.dashboard_orangtua'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Email atau password salah', 'error')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Validasi input dasar sebelum memanggil service
        if not all([nama, email, password, role]):
            flash('Semua kolom harus diisi.', 'error')
            return render_template('register.html')

        # Panggil service
        try:
            success, msg = service.create_user(
                nama=nama, 
                email=email, 
                password=password, 
                role=role, 
                student_id=None # Default None untuk pendaftaran mandiri
            )
            
            if success:
                flash('Akun berhasil dibuat! Silakan login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(msg, 'error')
        except Exception as e:
            print(f"Register Error: {e}")
            flash('Terjadi kesalahan internal server.', 'error')

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))