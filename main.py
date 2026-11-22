import sqlite3
import datetime
import csv
import os

DB_NAME = "evote_mahasiswa.db"
SQL_FILE = "database.sql"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==========================================
# 1. FUNGSI KONEKSI & INISIALISASI DATABASE
# ==========================================
def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    if os.path.exists(SQL_FILE):
        with open(SQL_FILE, "r", encoding="utf-8") as file:
            sql_script = file.read()
        cursor.executescript(sql_script)
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pemilih (
                nim TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                program_studi TEXT NOT NULL,
                angkatan INTEGER NOT NULL,
                sudah_memilih INTEGER DEFAULT 0,
                tanggal_vote TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kandidat (
                id_kandidat INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_calon TEXT NOT NULL,
                program_studi TEXT NOT NULL,
                angkatan INTEGER NOT NULL,
                visi TEXT NOT NULL,
                misi TEXT NOT NULL,
                total_suara INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pengaturan_pemilu (
                id INTEGER PRIMARY KEY,
                status_pemilu TEXT NOT NULL
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO admin (id, username, password) VALUES (1, 'admin', 'admin123')")
        cursor.execute("INSERT OR IGNORE INTO pengaturan_pemilu (id, status_pemilu) VALUES (1, 'AKTIF')")

        cursor.execute("SELECT COUNT(*) FROM kandidat")
        if cursor.fetchone()[0] == 0:
            kandidat_awal = [
                ("Dion Imanuel Putra", "Teknik Industri", 2026, "Mewujudkan Himpunan Mahasiswa Teknik Industri yang inovatif, adaptif, dan berdaya saing.", "1. Meningkatkan kompetensi keilmuan Teknik Industri\n2. Memperluas jejaring kolaborasi industri\n3. Transparansi dan efisiensi tata kelola organisasi", 0),
                ("Reza Ahmad", "Teknik Industri", 2026, "Membawa Himpunan Mahasiswa Teknik Industri menuju sistem kerja yang efektif dan berdampak.", "1. Optimalisasi sistem kerja organisasi\n2. Mendorong inovasi dan riset mahasiswa\n3. Meningkatkan kepedulian sosial masyarakat", 0),
                ("Kezia Awwliya", "Teknik Industri", 2026, "Menjadikan Himpunan Mahasiswa Teknik Industri lebih solid, produktif, dan prestatif.", "1. Memperkuat solidaritas antar angkatan\n2. Menghadirkan program kerja berkualitas\n3. Pengembangan soft skill dan kepemimpinan", 0)
            ]
            cursor.executemany('''
                INSERT INTO kandidat (nama_calon, program_studi, angkatan, visi, misi, total_suara)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', kandidat_awal)

        pemilih_lima_awal = [
            ('2610631140001', 'Dimas', 'Teknik Industri', 2026, 0, None),
            ('2610631140002', 'Rio', 'Teknik Industri', 2026, 0, None),
            ('2610631140003', 'Satria', 'Teknik Industri', 2026, 0, None),
            ('2610631140004', 'Hilman', 'Teknik Industri', 2026, 0, None),
            ('2610631140005', 'Gifari', 'Teknik Industri', 2026, 0, None)
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO pemilih (nim, nama, program_studi, angkatan, sudah_memilih, tanggal_vote)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', pemilih_lima_awal)

    cursor.execute("SELECT COUNT(*) FROM pemilih")
    jumlah_pemilih = cursor.fetchone()[0]
    if jumlah_pemilih < 500:
        pemilih_tambahan = []
        for i in range(6, 501):
            nim = f"261063114{i:04d}"
            nama = f"Mahasiswa TI {i}"
            pemilih_tambahan.append((nim, nama, "Teknik Industri", 2026, 0, None))
        cursor.executemany('''
            INSERT OR IGNORE INTO pemilih (nim, nama, program_studi, angkatan, sudah_memilih, tanggal_vote)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', pemilih_tambahan)

    conn.commit()
    conn.close()

def cek_status_pemilu():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status_pemilu FROM pengaturan_pemilu WHERE id = 1")
    status = cursor.fetchone()[0]
    conn.close()
    return status

# ==========================================
# 2. FUNGSI AUTENTIKASI (LOGIN)
# ==========================================
def login_mahasiswa():
    print("\n--- LOGIN MAHASISWA TEKNIK INDUSTRI ---")
    nim = input("Masukkan NIM : ").strip()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nim, nama, sudah_memilih FROM pemilih WHERE nim = ?", (nim,))
    data = cursor.fetchone()
    conn.close()

    if data is None:
        print("ERROR: NIM tidak terdaftar")
    else:
        print(f"Login Berhasil! Selamat datang, {data[1]}.")
        menu_mahasiswa(data[0])

def login_admin():
    print("\n--- LOGIN ADMIN PANITIA ---")
    username = input("Username : ").strip()
    password = input("Password : ").strip()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
    data = cursor.fetchone()
    conn.close()

    if data is None:
        print("ERROR: Username atau Password salah!")
    else:
        print("Login Admin Berhasil!")
        menu_admin()

# ==========================================
# 3. FUNGSI FITUR MAHASISWA (PEMILIH)
# ==========================================
def lihat_kandidat(detail=True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_kandidat, nama_calon, program_studi, angkatan, visi, misi FROM kandidat")
    kandidat_list = cursor.fetchall()
    conn.close()

    if not kandidat_list:
        print("\nBelum ada data kandidat.")
        return []

    print("\n============================================================")
    print(f"| {'No':<3} | {'Nama Kandidat':<26} | {'Angkatan':<10} |")
    print("============================================================")
    for idx, k in enumerate(kandidat_list, start=1):
        print(f"| {idx:<3} | {k[1]:<26} | {k[3]:<10} |")
    print("============================================================")

    if detail:
        for idx, k in enumerate(kandidat_list, start=1):
            print(f"\n[{idx}] {k[1]} ({k[2]} - {k[3]})")
            print(f"    Visi : {k[4]}")
            print(f"    Misi :\n    {k[5].replace(chr(10), chr(10)+'    ')}")
    
    return kandidat_list

def proses_voting(nim):
    if cek_status_pemilu() == "DITUTUP":
        print("\nPemungutan suara telah ditutup.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sudah_memilih FROM pemilih WHERE nim = ?", (nim,))
    sudah_memilih = cursor.fetchone()[0]

    if sudah_memilih == 1:
        print("\nAKSES DITOLAK")
        print("Anda sudah menggunakan hak suara.")
        conn.close()
        return

    kandidat_list = lihat_kandidat(detail=True)
    if not kandidat_list:
        conn.close()
        return

    try:
        pilihan = int(input("\nPilih Kandidat (masukkan nomor urut) : "))
        if pilihan < 1 or pilihan > len(kandidat_list):
            print("Pilihan tidak valid!")
            conn.close()
            return
    except ValueError:
        print("Input harus berupa angka!")
        conn.close()
        return

    kandidat_terpilih = kandidat_list[pilihan - 1]
    id_kandidat = kandidat_terpilih[0]
    nama_kandidat = kandidat_terpilih[1]

    print(f"\nAnda memilih: {nama_kandidat}")
    konfirmasi = input("Yakin? (Y/T) : ").strip().upper()

    if konfirmasi == 'Y':
        waktu_sekarang = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        cursor.execute("UPDATE kandidat SET total_suara = total_suara + 1 WHERE id_kandidat = ?", (id_kandidat,))
        cursor.execute("UPDATE pemilih SET sudah_memilih = 1, tanggal_vote = ? WHERE nim = ?", (waktu_sekarang, nim))
        conn.commit()
        print("\nTerima kasih.")
        print("Suara Anda berhasil direkam.")
    else:
        print("\nPemilihan dibatalkan.")

    conn.close()

def cek_status_voting(nim):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama, program_studi, sudah_memilih, tanggal_vote FROM pemilih WHERE nim = ?", (nim,))
    data = cursor.fetchone()
    conn.close()

    print("\n--- STATUS VOTING ANDA ---")
    print(f"NIM           : {nim}")
    print(f"Nama          : {data[0]}")
    print(f"Program Studi : {data[1]}")
    if data[2] == 1:
        print("Status Akun   : SUDAH MEMILIH")
        print(f"Waktu Vote    : {data[3]}")
    else:
        print("Status Akun   : BELUM MEMILIH")

def menu_mahasiswa(nim):
    while True:
        print("\n===== MENU PEMILIH =====")
        print("1. Lihat Kandidat")
        print("2. Voting")
        print("3. Status Voting")
        print("4. Logout")
        pilihan = input("Pilih menu : ").strip()

        if pilihan == '1':
            lihat_kandidat(detail=True)
        elif pilihan == '2':
            proses_voting(nim)
        elif pilihan == '3':
            cek_status_voting(nim)
        elif pilihan == '4':
            print("Logout berhasil.")
            break
        else:
            print("Pilihan tidak valid!")
# ==========================================
# 4. FUNGSI FITUR ADMIN (PANITIA)
# ==========================================
def kelola_kandidat():
    while True:
        print("\n--- KELOLA KANDIDAT ---")
        print("1. Lihat Daftar Kandidat")
        print("2. Tambah Kandidat")
        print("3. Ubah Data Kandidat")
        print("4. Hapus Kandidat")
        print("5. Kembali")
        pilih = input("Pilih menu : ").strip()

        conn = get_connection()
        cursor = conn.cursor()

        if pilih == '1':
            lihat_kandidat(detail=True)
        elif pilih == '2':
            print("\n-- Tambah Kandidat Baru --")
            nama = input("Nama Calon    : ")
            prodi = input("Program Studi (default: Teknik Industri) : ").strip() or "Teknik Industri"
            try:
                angkatan = int(input("Angkatan      : "))
            except ValueError:
                print("Angkatan harus berupa angka!")
                conn.close()
                continue
            visi = input("Visi          : ")
            misi = input("Misi          : ")
            cursor.execute('''
                INSERT INTO kandidat (nama_calon, program_studi, angkatan, visi, misi, total_suara)
                VALUES (?, ?, ?, ?, ?, 0)
            ''', (nama, prodi, angkatan, visi, misi))
            conn.commit()
            print("Kandidat berhasil ditambahkan!")
        elif pilih == '3':
            lihat_kandidat(detail=False)
            nama_lama = input("Masukkan Nama Calon yang ingin diubah : ")
            cursor.execute("SELECT id_kandidat FROM kandidat WHERE nama_calon = ?", (nama_lama,))
            row = cursor.fetchone()
            if row:
                nama_baru = input("Nama Calon Baru    : ")
                prodi_baru = input("Program Studi Baru (default: Teknik Industri) : ").strip() or "Teknik Industri"
                try:
                    angkatan_baru = int(input("Angkatan Baru      : "))
                except ValueError:
                    print("Angkatan harus berupa angka!")
                    conn.close()
                    continue
                visi_baru = input("Visi Baru          : ")
                misi_baru = input("Misi Baru          : ")
                cursor.execute('''
                    UPDATE kandidat 
                    SET nama_calon = ?, program_studi = ?, angkatan = ?, visi = ?, misi = ?
                    WHERE id_kandidat = ?
                ''', (nama_baru, prodi_baru, angkatan_baru, visi_baru, misi_baru, row[0]))
                conn.commit()
                print("Data kandidat berhasil diperbarui!")
            else:
                print("Kandidat tidak ditemukan.")
        elif pilih == '4':
            lihat_kandidat(detail=False)
            nama_hapus = input("Masukkan Nama Calon yang ingin dihapus : ")
            cursor.execute("DELETE FROM kandidat WHERE nama_calon = ?", (nama_hapus,))
            if cursor.rowcount > 0:
                conn.commit()
                print("Kandidat berhasil dihapus!")
            else:
                print("Kandidat tidak ditemukan.")
        elif pilih == '5':
            conn.close()
            break
        else:
            print("Pilihan tidak valid!")
        conn.close()

def tambah_pemilih():
    print("\n-- TAMBAH DATA PEMILIH BARU --")
    nim = input("Masukkan NIM Baru : ").strip()
    nama = input("Nama Lengkap      : ").strip()
    prodi = input("Program Studi (default: Teknik Industri) : ").strip() or "Teknik Industri"
    try:
        angkatan = int(input("Angkatan          : "))
    except ValueError:
        print("Angkatan harus berupa angka!")
        return

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO pemilih (nim, nama, program_studi, angkatan, sudah_memilih, tanggal_vote)
            VALUES (?, ?, ?, ?, 0, NULL)
        ''', (nim, nama, prodi, angkatan))
        conn.commit()
        print(f"Berhasil! Pemilih {nama} ({nim}) telah terdaftar dan siap digunakan login.")
    except sqlite3.IntegrityError:
        print("ERROR: NIM tersebut sudah terdaftar di database!")
    finally:
        conn.close()

def kelola_data_pemilih():
    while True:
        print("\n--- KELOLA DATA PEMILIH ---")
        print("1. Lihat Daftar Pemilih (20 Data Pertama)")
        print("2. Tambah Pemilih Baru (Daftarkan NIM & Nama)")
        print("3. Kembali")
        pilih = input("Pilih menu : ").strip()

        if pilih == '1':
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nim, nama, program_studi, sudah_memilih, tanggal_vote FROM pemilih LIMIT 20")
            rows = cursor.fetchall()
            conn.close()

            print("\n--- DATA PEMILIH TEKNIK INDUSTRI ---")
            print(f"{'NIM':<15} | {'Nama':<20} | {'Status':<14} | {'Waktu Vote'}")
            print("-" * 70)
            for r in rows:
                status = "SUDAH MEMILIH" if r[3] == 1 else "BELUM MEMILIH"
                waktu = r[4] if r[4] else "-"
                print(f"{r[0]:<15} | {r[1]:<20} | {status:<14} | {waktu}")
        elif pilih == '2':
            tambah_pemilih()
        elif pilih == '3':
            break
        else:
            print("Pilihan tidak valid!")

def tampilkan_hasil_voting():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_calon, total_suara FROM kandidat")
    data = cursor.fetchall()
    conn.close()

    total_semua_suara = sum(row[1] for row in data)

    print("\n==================================================")
    print("   HASIL VOTING KETUA HIMPUNAN TEKNIK INDUSTRI    ")
    print("==================================================")
    print(f"| {'Kandidat':<24} | {'Suara':<8} | {'Persentase':<10} |")
    print("--------------------------------------------------")
    
    for nama, suara in data:
        persen = (suara / total_semua_suara * 100) if total_semua_suara > 0 else 0
        print(f"| {nama:<24} | {suara:<8} | {persen:>8.1f}% |")
    print("==================================================")

    print("\nGRAFIK ASCII HASIL VOTING:")
    for nama, suara in data:
        persen = (suara / total_semua_suara * 100) if total_semua_suara > 0 else 0
        panjang_bar = int(persen // 2.5)
        bar = "█" * panjang_bar
        print(f"{nama:<20} : {bar} {persen:.1f}%")

    ekspor = input("\nExport hasil ke file CSV? (Y/T) : ").strip().upper()
    if ekspor == 'Y':
        with open("hasil_voting_ti.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Nama Kandidat", "Total Suara", "Persentase (%)"])
            for nama, suara in data:
                persen = (suara / total_semua_suara * 100) if total_semua_suara > 0 else 0
                writer.writerow([nama, suara, f"{persen:.2f}"])
        print("Data berhasil diekspor ke 'hasil_voting_ti.csv'!")

def tampilkan_statistik_pemilih():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pemilih")
    total_pemilih = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pemilih WHERE sudah_memilih = 1")
    sudah_memilih = cursor.fetchone()[0]
    conn.close()

    belum_memilih = total_pemilih - sudah_memilih
    partisipasi = (sudah_memilih / total_pemilih * 100) if total_pemilih > 0 else 0

    print("\n--- STATISTIK PEMILIH TEKNIK INDUSTRI ---")
    print(f"Total Pemilih Terdaftar : {total_pemilih}")
    print(f"Sudah Memilih           : {sudah_memilih}")
    print(f"Belum Memilih           : {belum_memilih}")
    print(f"Tingkat Partisipasi     : {partisipasi:.1f}%")

def tutup_pemilu():
    status = cek_status_pemilu()
    if status == "DITUTUP":
        print("\nStatus pemilu saat ini sudah DITUTUP.")
    else:
        konfirmasi = input("\nApakah Anda yakin ingin menutup pemungutan suara? (Y/T) : ").strip().upper()
        if konfirmasi == 'Y':
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE pengaturan_pemilu SET status_pemilu = 'DITUTUP' WHERE id = 1")
            conn.commit()
            conn.close()
            print("Pemungutan suara telah ditutup.")
        else:
            print("Penutupan dibatalkan.")
            return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_calon, total_suara FROM kandidat ORDER BY total_suara DESC")
    hasil = cursor.fetchall()
    conn.close()

    total_suara = sum(row[1] for row in hasil)
    if hasil and total_suara > 0:
        pemenang = hasil[0][0]
        suara_pemenang = hasil[0][1]
        persentase = (suara_pemenang / total_suara) * 100

        print("\n=========================================")
        print("   HASIL PEMILIHAN KETUA HIMPUNAN TI     ")
        print("=========================================")
        print(f"Pemenang    : {pemenang}")
        print(f"Total Suara : {suara_pemenang}")
        print(f"Persentase  : {persentase:.1f}%")
        print("=========================================")
    else:
        print("\nBelum ada suara yang masuk.")

def menu_admin():
    while True:
        print("\n===== DASHBOARD ADMIN =====")
        print("1. Kelola Kandidat")
        print("2. Data Pemilih")
        print("3. Hasil Voting")
        print("4. Statistik Voting")
        print("5. Tutup Pemilu")
        print("6. Logout")
        pilihan = input("Pilih menu : ").strip()

        if pilihan == '1':
            kelola_kandidat()
        elif pilihan == '2':
            kelola_data_pemilih()
        elif pilihan == '3':
            tampilkan_hasil_voting()
        elif pilihan == '4':
            tampilkan_statistik_pemilih()
        elif pilihan == '5':
            tutup_pemilu()
        elif pilihan == '6':
            print("Logout Admin berhasil.")
            break
        else:
            print("Pilihan tidak valid!")

# ==========================================
# 5. MENU UTAMA PROGRAM
# ==========================================
def main():
    clear_screen()
    init_db()
    while True:
        print("\n===== E-VOTE HIMPUNAN TEKNIK INDUSTRI =====")
        print("1. Login Mahasiswa")
        print("2. Login Admin")
        print("3. Keluar")
        pilihan = input("Pilih menu : ").strip()

        if pilihan == '1':
            login_mahasiswa()
        elif pilihan == '2':
            login_admin()
        elif pilihan == '3':
            print("Terima kasih telah menggunakan E-VOTE HIMPUNAN TEKNIK INDUSTRI.")
            break
        else:
            print("Pilihan tidak valid! Silakan coba lagi.")

if __name__ == "__main__":
    main()
