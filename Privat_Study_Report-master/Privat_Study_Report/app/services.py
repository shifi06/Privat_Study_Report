import uuid
from .repository import JsonRepository

class ReportService:
    """Business Logic Layer"""
    
    def __init__(self, repo: JsonRepository):
        self.repo = repo

    def create_report(self, guru_id, student_id, mata_pelajaran, materi, nilai, catatan, tanggal):
        if not student_id or not mata_pelajaran:
            return False, "Data tidak lengkap"
        
        try:
            nilai = int(nilai)
        except ValueError:
            return False, "Nilai harus berupa angka"

        report_data = {
            "id": f"r{str(uuid.uuid4())[:8]}",
            "guru_id": guru_id,
            "student_id": student_id,
            "tanggal": tanggal,
            "mata_pelajaran": mata_pelajaran,
            "materi": materi,
            "nilai": nilai,
            "catatan": catatan
        }
        
        self.repo.add_report(report_data)
        return True, "Laporan berhasil dibuat"

    def create_student(self, nama, kelas, orangtua_id=None):
        if not nama or not kelas:
            return False, "Nama dan Kelas harus diisi"
        
        student_id = f"s{str(uuid.uuid4())[:8]}"
        student_data = {
            "id": student_id,
            "nama": nama,
            "kelas": kelas,
            "orangtua_id": orangtua_id # Link ke orang tua di sini
        }
        self.repo.add_student(student_data)
        return True, "Berhasil menambahkan siswa baru"

    # --- PERBAIKAN UTAMA DI SINI ---
    def create_user(self, nama, email, password, role, student_id=None):
        # 1. Validasi input
        if not nama or not email or not password or not role:
            return False, "Semua field harus diisi"
        
        # 2. Cek duplikasi email
        if self.repo.get_user_by_email(email):
            return False, "Email sudah terdaftar"

        # 3. Buat user data dengan penanganan student_id yang aman
        user_id = f"u{str(uuid.uuid4())[:8]}"
        
        # Pastikan student_id benar-benar None jika string kosong atau role bukan orangtua
        final_student_id = None
        if role == 'orangtua' and student_id:
            final_student_id = student_id

        user_data = {
            "id": user_id,
            "nama": nama,
            "email": email,
            "password": password, # Plain text sesuai request
            "role": role,
            "student_id": final_student_id # Aman: None atau ID valid
        }
        
        try:
            self.repo.add_user(user_data)
            return True, "Pengguna berhasil ditambahkan"
        except Exception as e:
            print(f"Service Error (create_user): {e}")
            return False, f"Gagal menyimpan: {str(e)}"

    def get_student_report_summary(self, student_id):
        if not student_id:
            return {
                "student": {"nama": "Belum Terhubung", "kelas": "-"},
                "reports": [],
                "average_score": 0,
                "total_reports": 0
            }

        reports = self.repo.get_reports_by_student(student_id)
        student = self.repo.get_student_by_id(student_id)
        
        if not student:
             return {
                "student": {"nama": "Data Siswa Tidak Ditemukan", "kelas": "-"},
                "reports": [],
                "average_score": 0,
                "total_reports": 0
            }

        avg_score = 0
        if reports:
            total = sum(r['nilai'] for r in reports)
            avg_score = total / len(reports)

        return {
            "student": student,
            "reports": reports,
            "average_score": round(avg_score, 1),
            "total_reports": len(reports)
        }

# services.py

    def update_report(self, report_id, student_id, mata_pelajaran, materi, nilai, catatan, tanggal):
        """
        Memproses permintaan update laporan dengan validasi.
        """
        # 1. Validasi Input
        if not report_id or not student_id or not nilai:
            return False, "Data tidak lengkap. ID Laporan, Siswa, dan Nilai wajib diisi."

        try:
            nilai_int = int(nilai)
            if not (0 <= nilai_int <= 100):
                return False, "Nilai harus antara 0 sampai 100."
        except ValueError:
            return False, "Format nilai tidak valid."

        # 2. Siapkan data baru
        updated_data = {
            'student_id': student_id,
            'mata_pelajaran': mata_pelajaran,
            'materi': materi,
            'nilai': nilai_int,
            'catatan': catatan,
            'tanggal': tanggal
        }

        # 3. Panggil fungsi update di repository
        # Pastikan report_id dikirim dengan benar (misal: 'r123456')
        success = self.repo.update_report(report_id, updated_data)

        if success:
            return True, "Laporan berhasil diperbarui."
        else:
            return False, "Gagal memperbarui: ID Laporan tidak ditemukan di database."