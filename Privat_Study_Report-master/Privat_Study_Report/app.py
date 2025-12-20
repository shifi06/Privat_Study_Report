from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = "kunci_rahasia_bebas"

# Fungsi baca data dari file JSON
def load_data():
    with open('database.json', 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form.get('username')
        pass_input = request.form.get('password')
        
        data = load_data()
        # Cari user di JSON
        user = next((u for u in data['users'] if u['username'] == user_input and u['password'] == pass_input), None)
        
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('parent_dashboard'))
        return "Username atau Password Salah!"
    
    return render_template('login.html')

@app.route('/dashboard-orang-tua')
def parent_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    data = load_data()
    # Cari data anak berdasarkan user_id orang tua
    student = next((s for s in data['students'] if s['parent_id'] == session['user_id']), None)
    
    if student:
        # Ambil laporan
        reports = [r for r in data['reports'] if r['student_id'] == student['id']]
        # Hitung rata-rata
        avg = sum(r['nilai'] for r in reports) / len(reports) if reports else 0
        return render_template('parent_dashboard.html', student=student, reports=reports, average_score=round(avg, 1))
    
    return render_template('parent_dashboard.html', student=None)

if __name__ == '__main__':
    app.run(debug=True)