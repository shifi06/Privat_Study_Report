# Sistem Report Perkembangan Belajar Privat

Aplikasi ini dibangun berdasarkan proposal "Sistem Report Perkembangan Belajar Privat" untuk mempermudah pelaporan hasil belajar siswa privat kepada orang tua.

## Stok Teknologi

## Aktor dan Fitur

1. Admin

- Mengelola data pengguna (Guru & Orang Tua).

- Mengelola data siswa.

- Melihat ringkasan sistem.

2. Guru (Teacher)

- Input Laporan: Memasukkan nilai, materi yang diajarkan, dan catatan perkembangan.

- Riwayat Mengajar: Melihat laporan yang sudah dibuat.

3. Orang Tua (Parent)

- Monitoring: Melihat laporan perkembangan belajar anak.

- Evaluasi: Melihat rata-rata nilai dan catatan guru.

## Cara Menjalankan

1. Pastikan Python terinstall.

2. Install library:

```bash
pip install Flask Flask-Login
```

3. Jalankan aplikasi:

```bash
python run.py
```

4. Akses di browser: http://127.0.0.1:5000

## Akun Login (Default)

Password menggunakan Plain Text (tidak di-hash).

| Role| Email| Password |
|--------|---------|---------|
| Admin | admin@sekolah.com  | admin123   |
| Guru | guru@sekolah.com   | guru123   |
| Orang Tua | ortu@sekolah.com  | ortu123   |