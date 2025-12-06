
import os
from app import create_app

# Setup folder instance untuk database jika diperlukan
instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'instance')
if not os.path.exists(instance_path):
    try:
        os.makedirs(instance_path)
    except OSError as e:
        print(f"Error creating instance directory: {e}")

app = create_app()

if __name__ == '__main__':
    # use_reloader=False agar file JSON tidak rusak saat ditulis ulang otomatis
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)


