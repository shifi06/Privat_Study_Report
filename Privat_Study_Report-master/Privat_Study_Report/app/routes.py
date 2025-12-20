from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response
from flask_login import login_required, current_user
from . import service, repo
import csv
import uuid
import codecs
from io import StringIO
from datetime import datetime

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

# --- DASHBOARD GURU (DENGAN FILTER PRIVASI) ---
@main_bp.route('/dashboard/guru', methods=['GET', 'POST'])
@login_required
def dashboard_guru():
    if current_user.role != 'guru':
        return redirect(url_for('main.index'))

    daftar_mapel = [
        'Matematika', 'Bahasa Indonesia', 'Bahasa Inggris', 
        'IPA', 'IPS', 'Fisika', 'Kimia', 'Biologi', 
        'Sejarah', 'Informatika', 'Seni Budaya', 'Lainnya'
    ]

    # 1. Ambil data mentah
    all_students = repo.get_all_students()
    all_reports = repo.get_all_reports()

    # 2. FILTER: Hanya ambil siswa yang dibimbing oleh GURU INI
    students = [s for s in all_students if s.get('teacher_id') == current_user.id]
    my_student_ids = [s['id'] for s in students]

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'delete_report':
            report_id = request.form.get('report_id')
            repo.delete_report(report_id)
            flash('Laporan berhasil dihapus!', 'success')
            return redirect(url_for('main.dashboard_guru'))

        elif action == 'edit_report':
            report_id = request.form.get('report_id')
            data = {
                'student_id': request.form.get('student_id'),
                'tanggal': request.form.get('tanggal'),
                'nilai': request.form.get('nilai'),
                'mata_pelajaran': request.form.get('mapel'),
                'materi': request.form.get('materi'),
                'catatan': request.form.get('catatan')
            }
            repo.update_report(report_id, data)
            flash('Laporan berhasil diperbarui!', 'success')
            return redirect(url_for('main.dashboard_guru'))

        elif action == 'create_report':
            data = {
                'student_id': request.form.get('student_id'),
                'tanggal': request.form.get('tanggal'),
                'nilai': request.form.get('nilai'),
                'mata_pelajaran': request.form.get('mapel'),
                'materi': request.form.get('materi'),
                'catatan': request.form.get('catatan')
            }
            repo.add_report(data)
            flash('Laporan baru berhasil disimpan!', 'success')
            return redirect(url_for('main.dashboard_guru'))

    # 3. FILTER LAPORAN: Hanya tampilkan laporan untuk siswa bimbingan guru ini
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    reports = []
    for r in all_reports:
        # Cek apakah ID siswa di laporan ada dalam daftar murid guru ini
        if r['student_id'] in my_student_ids:
            s = repo.get_student_by_id(r['student_id'])
            r['nama_siswa'] = s['nama'] if s else "Unknown"

            if start_date and end_date:
                if start_date <= r.get('tanggal', '') <= end_date:
                    reports.append(r)
            else:
                reports.append(r)

    reports = sorted(reports, key=lambda x: x.get('tanggal', ''), reverse=True)

    return render_template(
        'dashboard_guru.html', 
        students=students, 
        reports=reports, 
        daftar_mapel=daftar_mapel,
        start_date=start_date,
        end_date=end_date
    )

# --- DASHBOARD ORANG TUA ---
@main_bp.route('/dashboard/orangtua')
@login_required
def dashboard_orangtua():
    if current_user.role != 'orangtua':
        return redirect(url_for('main.index'))
    
    # 1. Ambil data mentah dari DB
    db_data = repo._read_db()
    all_users = db_data.get('users', {})
    all_students = db_data.get('students', {})
    all_reports = db_data.get('reports', {})

    # 2. Ambil daftar Guru untuk dropdown
    teachers = [u for u in all_users.values() if u.get('role') == 'guru']
    
    # 3. Ambil daftar anak milik orang tua ini
    my_children = [s for s in all_students.values() if s.get('parent_id') == current_user.id]
    
    # 4. Tentukan anak mana yang sedang dilihat (default anak pertama)
    selected_student_id = request.args.get('student_id')
    selected_student = None
    
    if selected_student_id:
        selected_student = all_students.get(selected_student_id)
    elif my_children:
        selected_student = my_children[0]
    
    # 5. Ambil laporan dan hitung rata-rata
    reports = []
    avg_score = 0
    if selected_student:
        reports = [r for r in all_reports.values() if r.get('student_id') == selected_student['id']]
        if reports:
            avg_score = sum(int(r.get('nilai', 0)) for r in reports) // len(reports)

    return render_template('dashboard_orangtua.html', 
    student=selected_student, 
    my_children=my_children,
    all_teachers=teachers,
    reports=reports, 
    average_score=avg_score,
    total_reports=len(reports))

# --- FITUR TAMBAH ANAK ---
@main_bp.route('/tambah-anak', methods=['POST'])
@login_required
def tambah_anak():
    nama_anak = request.form.get('nama_anak')
    kelas = request.form.get('kelas')
    teacher_id = request.form.get('teacher_id')
    
    if nama_anak and teacher_id:
        student_id = f"s{str(uuid.uuid4())[:8]}"
        new_student = {
            "id": student_id,
            "nama": nama_anak,
            "kelas": kelas if kelas else "Umum",
            "parent_id": current_user.id,
            "teacher_id": teacher_id
        }
        
        data = repo._read_db()
        data['students'][student_id] = new_student
        repo._write_db(data)
        
        flash(f"Berhasil mendaftarkan {nama_anak}!", "success")
    else:
        flash("Gagal mendaftarkan anak. Pastikan semua field terisi.", "danger")
    
    return redirect(url_for('main.dashboard_orangtua'))

# --- EXPORT DATA CSV ---
@main_bp.route('/export-reports')
@login_required
def export_reports():
    reports = repo.get_all_reports()
    si = StringIO()
    si.write("sep=;\n") 
    si.write(codecs.BOM_UTF8.decode('utf-8'))
    cw = csv.writer(si, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    
    cw.writerow(['TANGGAL', 'NAMA SISWA', 'MATA PELAJARAN', 'MATERI POKOK', 'NILAI', 'STATUS', 'CATATAN PERKEMBANGAN'])
    
    for r in reports:
        s = repo.get_student_by_id(r['student_id'])
        nama_siswa = s['nama'].upper() if s else "TIDAK DIKENAL"
        nilai = int(r.get('nilai', 0))
        status = "LULUS" if nilai >= 75 else "REMEDIAL"
        
        cw.writerow([
            r.get('tanggal', '-'),
            nama_siswa,
            r.get('mata_pelajaran', '-'),
            r.get('materi', '-'),
            nilai,
            status,
            r.get('catatan', '-')
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Laporan_Mengajar.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output

# --- DASHBOARD ADMIN ---
@main_bp.route('/dashboard/admin')
@login_required
def dashboard_admin():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    db_data = repo._read_db()
    users_dict = db_data.get('users', {})
    students_dict = db_data.get('students', {})
    reports_dict = db_data.get('reports', {})

    # 1. Siapkan List User
    users_list = list(users_dict.values())

    # 2. Siapkan List Siswa dengan Nama Orang Tua & Guru
    students_list = []
    for s in students_dict.values():
        parent = users_dict.get(s.get('parent_id'), {})
        teacher = users_dict.get(s.get('teacher_id'), {})
        
        s_data = s.copy()
        s_data['nama_orangtua'] = parent.get('nama', 'Tidak Ada')
        s_data['nama_guru'] = teacher.get('nama', 'Belum Dipilih')
        students_list.append(s_data)

    return render_template('dashboard_admin.html', 
                           users=users_list, 
                           students=students_list, 
                           report_count=len(reports_dict),
                           now=datetime.now())

@main_bp.route('/admin/delete-user/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    db_data = repo._read_db()
    if user_id in db_data['users']:
        del db_data['users'][user_id]
        # Hapus juga data murid jika user tersebut adalah orang tua (opsional)
        repo._write_db(db_data)
        flash("Pengguna berhasil dihapus.", "success")
    
    return redirect(url_for('main.dashboard_admin'))
    