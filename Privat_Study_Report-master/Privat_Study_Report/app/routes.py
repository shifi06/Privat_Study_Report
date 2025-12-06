from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import service, repo

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.role == 'admin':
        return redirect(url_for('main.dashboard_admin'))
    elif current_user.role == 'guru':
        return redirect(url_for('main.dashboard_guru'))
    elif current_user.role == 'orangtua':
        return redirect(url_for('main.dashboard_orangtua'))
    
    return "Role tidak dikenali"

# --- DASHBOARD ADMIN ---
@main_bp.route('/dashboard/admin') # Menghapus methods=['POST'] karena fitur tambah pengguna dihapus
@login_required
def dashboard_admin():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    # Logika POST untuk 'create_user' telah dihapus sesuai permintaan
        
    users = repo.get_all_users()
    students = repo.get_all_students()
    reports = repo.get_all_reports()
    
    from datetime import datetime
    return render_template('dashboard_admin.html', users=users, students=students, report_count=len(reports), now=datetime.now())

# --- DASHBOARD GURU ---
@main_bp.route('/dashboard/guru', methods=['GET', 'POST'])
@login_required
def dashboard_guru():
    if current_user.role != 'guru':
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create_report':
            # Proses Input Laporan
            success, msg = service.create_report(
                guru_id=current_user.id,
                student_id=request.form.get('student_id'),
                mata_pelajaran=request.form.get('mapel'),
                materi=request.form.get('materi'),
                nilai=request.form.get('nilai'),
                catatan=request.form.get('catatan'),
                tanggal=request.form.get('tanggal')
            )
            if success:
                flash(msg, 'success')
            else:
                flash(msg, 'error')
                
        elif action == 'create_student':
            # Proses Input Siswa Baru
            success, msg = service.create_student(
                nama=request.form.get('nama'),
                kelas=request.form.get('kelas')
            )
            if success:
                flash(msg, 'success')
            else:
                flash(msg, 'error')
                
        return redirect(url_for('main.dashboard_guru'))

    # Data untuk tampilan
    students = repo.get_all_students()
    reports = repo.get_all_reports() 
    
    # Tambahkan nama siswa ke laporan untuk tampilan
    for r in reports:
        s = repo.get_student_by_id(r['student_id'])
        r['nama_siswa'] = s['nama'] if s else "Unknown"

    return render_template('dashboard_guru.html', students=students, reports=reports)

# --- DASHBOARD ORANG TUA ---
@main_bp.route('/dashboard/orangtua')
@login_required
def dashboard_orangtua():
    if current_user.role != 'orangtua':
        return redirect(url_for('main.index'))
    
    # Ambil data anak dari link di user
    student_id = current_user.student_id
    if not student_id:
        return "Akun ini belum terhubung dengan data siswa."
        
    data = service.get_student_report_summary(student_id)
    
    return render_template('dashboard_orangtua.html', **data)