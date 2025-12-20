import json
import os
import uuid
class JsonRepository:
    """Data Access Layer: Menangani interaksi langsung dengan file JSON"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        if not os.path.exists(db_path):
            self._write_db({"users": {}, "students": {}, "reports": {}})

    def _read_db(self):
        try:
            with open(self.db_path, 'r') as f:
                content = f.read()
                if not content:
                    return {"users": {}, "students": {}, "reports": {}}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": {}, "students": {}, "reports": {}}

    def _write_db(self, data):
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Repository Write Error: {e}")
            raise # Lempar error agar bisa ditangkap di service

    # --- Users ---
    def get_user_by_email(self, email):
        data = self._read_db()
        # Pastikan 'users' ada di dictionary
        users = data.get('users', {})
        for user in users.values():
            if user.get('email') == email:
                return user
        return None

    def get_user_by_id(self, user_id):
        data = self._read_db()
        return data.get('users', {}).get(user_id)

    def get_all_users(self):
        data = self._read_db()
        return list(data.get('users', {}).values())

    def add_user(self, user_data):
        data = self._read_db()
        # Inisialisasi 'users' jika belum ada (untuk jaga-jaga file rusak)
        if 'users' not in data:
            data['users'] = {}
            
        data['users'][user_data['id']] = user_data
        self._write_db(data)
        return user_data

    # --- Students ---
    def get_all_students(self):
        data = self._read_db()
        return list(data.get('students', {}).values())
    
    def get_student_by_id(self, s_id):
        data = self._read_db()
        return data.get('students', {}).get(s_id)
    
    def add_student(self, student_data):
        data = self._read_db()
        if 'students' not in data:
            data['students'] = {}
        data['students'][student_data['id']] = student_data
        self._write_db(data)
        return student_data

    # --- Reports ---
    def add_report(self, report_data):
        """Menambah laporan baru dengan generate ID unik otomatis"""
        data = self._read_db()
        if 'reports' not in data:
            data['reports'] = {}
        
        # Jika ID tidak dikirim dari service, buat ID unik baru
        if 'id' not in report_data or not report_data['id']:
            report_data['id'] = str(uuid.uuid4())[:8]
            
        data['reports'][report_data['id']] = report_data
        self._write_db(data)
        return report_data

    def get_all_reports(self):
        data = self._read_db()
        return list(data.get('reports', {}).values())

    def update_report(self, report_id, updated_data):
        """Memperbarui laporan berdasarkan report_id"""
        data = self._read_db()
        
        if 'reports' in data and report_id in data['reports']:
            # Gunakan .update() untuk memperbarui dictionary secara efisien
            data['reports'][report_id].update(updated_data)
            self._write_db(data)
            return True
        return False

    def delete_report(self, report_id):
        """
        BARU: Menghapus laporan berdasarkan ID.
        Fungsi ini akan dipanggil oleh routes.py
        """
        data = self._read_db()
        
        # Pastikan report_id dikonversi ke string karena JSON key selalu string
        report_id = str(report_id)
        
        if 'reports' in data and report_id in data['reports']:
            # Menghapus key dari dictionary
            del data['reports'][report_id]
            self._write_db(data)
            return True
            
        return False
    
    # Tambahkan ini di class JsonRepository
def get_students_by_parent(self, parent_id):
    data = self._read_db()
    students = data.get('students', {})
    # Ambil semua siswa yang punya orangtua_id cocok
    return [s for s in students.values() if s.get('orangtua_id') == parent_id]