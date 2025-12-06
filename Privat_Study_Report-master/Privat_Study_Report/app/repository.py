import json
import os

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
        data = self._read_db()
        if 'reports' not in data:
            data['reports'] = {}
        data['reports'][report_data['id']] = report_data
        self._write_db(data)
        return report_data

    def get_reports_by_student(self, student_id):
        data = self._read_db()
        reports = []
        # Pastikan 'reports' ada
        all_reports = data.get('reports', {})
        for r in all_reports.values():
            if r.get('student_id') == student_id:
                reports.append(r)
        return sorted(reports, key=lambda x: x.get('tanggal', ''), reverse=True)

    def get_all_reports(self):
        data = self._read_db()
        return list(data.get('reports', {}).values())