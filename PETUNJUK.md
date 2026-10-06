# Ruang Biografi — petunjuk menjalankan

1. Ekstrak ZIP. Buka folder ai_biografi di VS Code.
2. Pada terminal dalam folder tersebut, jalankan:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Jika Windows tidak mengenali `python`, gunakan `py` untuk kedua perintah.
Buka alamat Local URL yang muncul di terminal. Hentikan server dengan Ctrl+C.

## Pertama kali
Buat akun **Guru** sebelum membagikan aplikasi. Akun guru pertama hanya tersedia saat belum ada guru. Guru berikutnya dibuat melalui Dashboard Guru. Mahasiswa mendaftar melalui tab Daftar, lalu masuk dengan peran Mahasiswa. Akun guru tidak ditampilkan dalam daftar mahasiswa.

## Mengisi materi
Pada Materi Biografi, pilih subbab → Tambah / edit materi → ketik atau impor TXT UTF-8 → isi sumber → Simpan perubahan. Subbab sengaja kosong karena sumber belum diberikan. File TXT lama juga dapat disalin ke folder database agar bisa dicari tutor. TXT lama tidak otomatis menjadi subbab.

## LKPD dan penilaian
Mahasiswa mengisi jawaban, menyimpan draf, kemudian mengirim jawaban lengkap. Guru melihat pekerjaan dan memberi nilai per komponen (total 100). Guru dapat membuka pekerjaan untuk revisi. Simpan materi berarti menandai materi; Unduh materi menyimpan salinan TXT. Modul Guru dapat diedit dan diunduh dalam Markdown.

## Penyimpanan dan penggunaan bersama
Akun, materi, penanda, modul, serta jawaban disimpan dalam data.sqlite3 di sebelah app.py. Data bertahan setelah aplikasi ditutup selama file ini tetap ada. Cadangkan file ketika server berhenti. Jangan menghapus atau membagikan database yang berisi data mahasiswa.

Mahasiswa harus mengakses **server aplikasi yang sama** agar guru melihat seluruh pekerjaan. Menyalin aplikasi ke laptop terpisah menghasilkan database yang berbeda. Untuk uji di jaringan Wi-Fi yang sama, jalankan:

```powershell
python -m streamlit run app.py --server.address 0.0.0.0
```

Gunakan Network URL dari terminal di perangkat mahasiswa. Akses dapat memerlukan izin firewall Windows. Jangan membuka port router ke internet. Untuk akses lintas lokasi diperlukan hosting dengan penyimpanan persisten, HTTPS, dan konfigurasi akun; hosting belum termasuk paket ini. Penyimpanan lokal pada hosting sementara dapat hilang.

## Tentang tutor
Program ini mempertahankan pendekatan awal: pencarian potongan materi lokal dan sumbernya. Tidak menggunakan model generatif, tidak memerlukan API key, dan tidak membuat jawaban saat materi kosong. Pencarian masih berbasis kata kunci; hasil tetap perlu diperiksa. Modul dan LKPD merupakan rancangan awal, bukan CP/CPMK resmi. Sesuaikan dengan mata kuliah serta teks biografi yang dipilih.

## Verifikasi
Sintaks Python, penyimpanan akun, autentikasi, pencarian lokal, dan pemisahan data diuji pada lingkungan pengembangan. Uji tampilan dan alur Streamlit diperlukan di komputer pengguna karena Streamlit belum tersedia dalam lingkungan pengembangan.
