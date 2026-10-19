
# Dashboard Toko Elektronik

Mini project dashboard inventaris toko elektronik menggunakan Vue 3 dan FastAPI.

## 1. Deskripsi

Aplikasi ini digunakan untuk melihat dan mengelola data produk elektronik. Pengguna dapat melihat ringkasan inventaris, mencari dan mengurutkan produk, memantau stok per kategori, serta menambah, mengubah, dan menghapus data produk.

Data produk disimpan pada file JSON melalui backend FastAPI.

## 2. Teknologi

- Frontend: Vue 3 Composition API
- Build tool frontend: Vite
- Backend: Python dan FastAPI
- Validasi data: Pydantic
- Penyimpanan: File JSON
- Komunikasi frontend-backend: Fetch API, async/await
- Tampilan: CSS responsif tanpa library grafik tambahan

## 3. Fitur Aplikasi

### Dashboard
- Total produk terdaftar.
- Jumlah produk dengan stok menipis atau habis.
- Jumlah kategori produk.
- Total unit stok seluruh produk.

### Pengelolaan Produk
- Menampilkan daftar produk.
- Mencari produk berdasarkan nama atau kategori.
- Mengurutkan nama produk dari A–Z atau Z–A.
- Menambah produk.
- Mengubah data produk.
- Menghapus produk.
- Menampilkan status stok.
- Menampilkan grafik batang jumlah stok per kategori.

### Kondisi Tampilan
- Menampilkan indikator saat data sedang dimuat.
- Menampilkan pesan ketika produk tidak ditemukan.
- Menampilkan pesan kesalahan apabila permintaan ke backend gagal.
- Menyesuaikan tampilan untuk desktop, tablet, dan perangkat mobile.

## 4. Aturan Status Stok

Status stok ditentukan berdasarkan jumlah unit:

- Habis: stok = 0.
- Menipis: stok 1 sampai 5.
- Tersedia: stok lebih dari 5.

Kartu "Stok Menipis + Habis" menghitung seluruh produk dengan stok kurang dari atau sama dengan 5, termasuk produk dengan stok 0.

## 5. Struktur Proyek

```text
dashboard-toko-elektronik/
├── backend/
│   ├── .venv/
│   ├── main.py
│   ├── products.json
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

## 6. Cara Menjalankan Backend

Pastikan Python sudah terpasang.

Buka terminal dan masuk ke folder backend:

```bash
cd backend
```

Buat virtual environment jika belum tersedia:

```bash
python3 -m venv .venv
```

Aktifkan virtual environment di macOS atau Linux:

```bash
source .venv/bin/activate
```

Instal dependensi:

```bash
pip install -r requirements.txt
```

Jalankan server:

```bash
python -m uvicorn main:app --reload
```

Backend berjalan pada:

- API: http://127.0.0.1:8000
- Dokumentasi API: http://127.0.0.1:8000/docs

## 7. Cara Menjalankan Frontend

Buka terminal baru dan masuk ke folder frontend dari direktori utama proyek:

```bash
cd frontend
```

Instal dependensi jika belum tersedia:

```bash
npm install
```

Jalankan aplikasi:

```bash
npm run dev
```

Buka alamat yang ditampilkan oleh Vite di terminal, biasanya:

http://localhost:5173

Backend dan frontend harus berjalan bersamaan agar dashboard dapat mengambil dan mengelola data.

## 8. Endpoint API

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/` | Memeriksa status backend |
| GET | `/products` | Mengambil seluruh produk |
| POST | `/products` | Menambahkan produk |
| PUT | `/products/{product_id}` | Memperbarui produk |
| DELETE | `/products/{product_id}` | Menghapus produk |

### Validasi Data

- Nama produk wajib diisi, maksimal 100 karakter.
- Kategori wajib diisi, maksimal 50 karakter.
- Stok harus berupa bilangan bulat dan tidak boleh negatif.
- Harga harus berupa bilangan bulat lebih dari 0.
- ID produk harus unik dan bernilai positif.

## 9. Penyimpanan Data

Data awal dan perubahan produk disimpan pada `backend/products.json`. Backend membaca file tersebut saat aplikasi dimulai dan menulis ulang file ketika produk ditambah, diubah, atau dihapus.

File JSON ini digunakan sebagai penyimpanan lokal untuk keperluan mini project.

## 10. Catatan

Pastikan dependensi backend dan frontend sudah diinstal sebelum menjalankan aplikasi. Jangan mengunggah folder virtual environment atau `node_modules` ke repositori Git.
