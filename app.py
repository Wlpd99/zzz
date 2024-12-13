from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Kontrakan, Penyewa, Transaksi, Pembayaran
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import json
import os
from decorators import login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost/kontrakan'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
users_db = {}
app.secret_key = '99'

# Nama file JSON untuk menyimpan data pengguna
USER_FILE = 'users.json'

# Fungsi untuk membaca data pengguna dari file JSON
def read_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)  # Mengembalikan dictionary berisi data pengguna
    except FileNotFoundError:
        return {}

# Fungsi untuk menulis data pengguna ke file JSON
def write_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

# Daftar halaman yang tidak memerlukan login
EXCLUDED_ROUTES = ['login', 'register', 'static', 'home', 'pesan', 'success']  # Tambahkan rute yang dikecualikan

@app.before_request
def check_login():
    # Jika rute saat ini tidak ada dalam EXCLUDED_ROUTES dan pengguna belum login
    if request.endpoint not in EXCLUDED_ROUTES and 'username' not in session:
        flash('Anda harus login untuk mengakses halaman ini.', 'warning')
        return redirect(url_for('login'))  # Arahkan ke halaman login


@app.route('/')
def home():
    kontrakans = Kontrakan.query.all()
    return render_template('home.html', kontrakans=kontrakans)

@app.route('/index')
def index():
    username = session.get('username') 
    return render_template('index.html', username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Ambil data pengguna dari file JSON
        users = read_users()

        # Cek apakah username ada dan password cocok
        if username in users and users[username] == password:
            session['username'] = username  # Menyimpan username di session
            flash('Login berhasil!', 'success')
            return redirect(url_for('index'))  # Redirect ke halaman home setelah login sukses
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Ambil data pengguna dari file JSON
        users= read_users()

        # Cek jika username sudah ada
        if username in users:
            flash('Username sudah terdaftar!', 'danger')
        else:
            # Menambahkan pengguna baru ke dictionary
            users[username] = password
            write_users(users)  # Menyimpan data pengguna ke file JSON
            flash('Registrasi berhasil!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  # Hapus sesi pengguna
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('home'))  # Arahkan ke halaman login

# Route untuk menampilkan semua kontrakan
@app.route('/kontrakan')
def kontrakan():
    kontrakans = Kontrakan.query.all()  # Ambil semua data kontrakan dari database
    return render_template('a_kontrakan.html', kontrakans=kontrakans)

# Route untuk menambah kontrakan baru
@app.route('/kontrakan/tambah', methods=['GET', 'POST'])
def tambah_kontrakan():
    if request.method == 'POST':
        alamat = request.form['alamat']
        fasilitas = request.form['fasilitas']
        harga_per_bulan = request.form['harga_per_bulan']
        status = request.form['status']
        
        # Membuat objek kontrakan baru dan menyimpannya di database
        kontrakan_baru = Kontrakan(
            alamat=alamat, 
            fasilitas=fasilitas, 
            harga_per_bulan=harga_per_bulan, 
            status=status
        )
        db.session.add(kontrakan_baru)
        db.session.commit()
        return redirect(url_for('kontrakan'))
    
    return render_template('tambah_kontrakan.html')

# Route untuk mengedit kontrakan
@app.route('/kontrakan/edit/<int:id>', methods=['GET', 'POST'])
def edit_kontrakan(id):
    kontrakan = Kontrakan.query.get_or_404(id)
    
    if request.method == 'POST':
        kontrakan.alamat = request.form['alamat']
        kontrakan.fasilitas = request.form['fasilitas']
        kontrakan.harga_per_bulan = request.form['harga_per_bulan']
        kontrakan.status = request.form['status']
        
        db.session.commit()
        return redirect(url_for('kontrakan'))
    
    return render_template('edit_kontrakan.html', kontrakan=kontrakan)

# Route untuk menghapus kontrakan
@app.route('/kontrakan/hapus/<int:id>', methods=['GET', 'POST'])
def delete_kontrakan(id):
    kontrakan = Kontrakan.query.get_or_404(id)
    if kontrakan:
        db.session.delete(kontrakan)
        db.session.commit()
    return redirect(url_for('kontrakan'))

@app.route('/penyewa')
def penyewa():
    penyewas = Penyewa.query.all()  # Ambil semua data penyewa dari database
    return render_template('a_penyewa.html', penyewas=penyewas)

# Route untuk menambah penyewa baru
@app.route('/penyewa/tambah', methods=['GET', 'POST'])
def tambah_penyewa():
    if request.method == 'POST':
        nama = request.form['nama']
        no_telepon = request.form['no_telepon']
        email = request.form['email']
        alamat = request.form['alamat']
        
        # Membuat objek penyewa baru dan menyimpannya di database
        penyewa_baru = Penyewa(
            nama=nama, 
            no_telepon=no_telepon, 
            email=email, 
            alamat=alamat
        )
        db.session.add(penyewa_baru)
        db.session.commit()
        return redirect(url_for('penyewa'))
    
    return render_template('tambah_penyewa.html')

# Route untuk mengedit penyewa
@app.route('/penyewa/edit/<int:id>', methods=['GET', 'POST'])
def edit_penyewa(id):
    penyewa = Penyewa.query.get_or_404(id)
    
    if request.method == 'POST':
        penyewa.nama = request.form['nama']
        penyewa.no_telepon = request.form['no_telepon']
        penyewa.email = request.form['email']
        penyewa.alamat = request.form['alamat']
        
        db.session.commit()
        return redirect(url_for('penyewa'))
    
    return render_template('edit_penyewa.html', penyewa=penyewa)

# Route untuk menghapus penyewa
@app.route('/penyewa/hapus/<int:id>', methods=['GET', 'POST'])
def delete_penyewa(id):
    penyewa = Penyewa.query.get_or_404(id)
    
    db.session.delete(penyewa)
    db.session.commit()
    return redirect(url_for('penyewa'))

# Route untuk menampilkan semua transaksi
@app.route('/transaksi')
def transaksi():
    transaksi_list = Transaksi.query.all()  # Ambil semua transaksi dari database
    return render_template('a_transaksi.html', transaksi_list=transaksi_list)

# Route untuk menambah transaksi baru
@app.route('/transaksi/tambah', methods=['GET', 'POST'])
def tambah_transaksi():
    if request.method == 'POST':
        id_kontrakan = request.form['id_kontrakan']
        id_penyewa = request.form['id_penyewa']
        tanggal_mulai = request.form['tanggal_mulai']
        tanggal_selesai = request.form['tanggal_selesai']
        total_pembayaran = request.form['total_pembayaran']
        
        # Membuat objek transaksi baru dan menyimpannya di database
        transaksi_baru = Transaksi(
            id_kontrakan=id_kontrakan,
            id_penyewa=id_penyewa,
            tanggal_mulai=tanggal_mulai,
            tanggal_selesai=tanggal_selesai,
            total_pembayaran=total_pembayaran
        )
        db.session.add(transaksi_baru)
        db.session.commit()
        return redirect(url_for('transaksi'))
    
    # Mengambil data kontrakan dan penyewa untuk form
    kontrakans = Kontrakan.query.all()
    penyewas = Penyewa.query.all()
    return render_template('tambah_transaksi.html', kontrakans=kontrakans, penyewas=penyewas)

# Route untuk mengedit transaksi
@app.route('/transaksi/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaksi(id):
    transaksi = Transaksi.query.get_or_404(id)
    
    if request.method == 'POST':
        transaksi.id_kontrakan = request.form['id_kontrakan']
        transaksi.id_penyewa = request.form['id_penyewa']
        transaksi.tanggal_mulai = request.form['tanggal_mulai']
        transaksi.tanggal_selesai = request.form['tanggal_selesai']
        transaksi.total_pembayaran = request.form['total_pembayaran']
        
        db.session.commit()
        return redirect(url_for('transaksi'))
    
    # Mengambil data kontrakan dan penyewa untuk form
    kontrakans = Kontrakan.query.all()
    penyewas = Penyewa.query.all()
    return render_template('edit_transaksi.html', transaksi=transaksi, kontrakans=kontrakans, penyewas=penyewas)

# Route untuk menghapus transaksi
@app.route('/transaksi/hapus/<int:id>', methods=['GET', 'POST'])
def delete_transaksi(id):
    transaksi = Transaksi.query.get_or_404(id)
    
    db.session.delete(transaksi)
    db.session.commit()
    return redirect(url_for('transaksi'))

# Route untuk menampilkan semua pembayaran
@app.route('/pembayaran')
def pembayaran():
    pembayaran_list = Pembayaran.query.all()  # Ambil semua pembayaran dari database
    return render_template('a_pembayaran.html', pembayaran_list=pembayaran_list)

# Route untuk menambah pembayaran baru
@app.route('/pembayaran/tambah', methods=['GET', 'POST'])
def tambah_pembayaran():
    if request.method == 'POST':
        id_transaksi = request.form['id_transaksi']
        tanggal_bayar = request.form['tanggal_bayar']
        jumlah_bayar = request.form['jumlah_bayar']
        
        # Membuat objek pembayaran baru dan menyimpannya di database
        pembayaran_baru = Pembayaran(
            id_transaksi=id_transaksi,
            tanggal_bayar=tanggal_bayar,
            jumlah_bayar=jumlah_bayar
        )
        db.session.add(pembayaran_baru)
        db.session.commit()
        return redirect(url_for('pembayaran'))
    
    # Mengambil data transaksi untuk form
    transaksi_list = Transaksi.query.all()
    return render_template('tambah_pembayaran.html', transaksi_list=transaksi_list)

# Route untuk mengedit pembayaran
@app.route('/pembayaran/edit/<int:id>', methods=['GET', 'POST'])
def edit_pembayaran(id):
    pembayaran = Pembayaran.query.get_or_404(id)
    
    if request.method == 'POST':
        pembayaran.id_transaksi = request.form['id_transaksi']
        pembayaran.tanggal_bayar = request.form['tanggal_bayar']
        pembayaran.jumlah_bayar = request.form['jumlah_bayar']
        
        db.session.commit()
        return redirect(url_for('pembayaran'))
    
    # Mengambil data transaksi untuk form
    transaksi_list = Transaksi.query.all()
    return render_template('edit_pembayaran.html', pembayaran=pembayaran, transaksi_list=transaksi_list)

# Route untuk menghapus pembayaran
@app.route('/pembayaran/hapus/<int:id>', methods=['GET', 'POST'])
def delete_pembayaran(id):
    pembayaran = Pembayaran.query.get_or_404(id)
    
    db.session.delete(pembayaran)
    db.session.commit()
    return redirect(url_for('pembayaran'))

@app.route('/pesan/<int:id_kontrakan>', methods=['GET', 'POST'])
def pesan(id_kontrakan):
    kontrakan = Kontrakan.query.get_or_404(id_kontrakan)
    
    if request.method == 'POST':
        # Ambil data dari form
        nama = request.form['nama']
        no_telepon = request.form['no_telepon']
        email = request.form.get('email')
        alamat = request.form.get('alamat')
        tanggal_mulai = request.form['tanggal_mulai']
        tanggal_selesai = request.form['tanggal_selesai']
        jumlah_bayar = request.form['jumlah_bayar']
        
        # Simpan data penyewa
        penyewa = Penyewa(nama=nama, no_telepon=no_telepon, email=email, alamat=alamat)
        db.session.add(penyewa)
        db.session.commit()

        # Simpan data transaksi
        transaksi = Transaksi(id_kontrakan=id_kontrakan, id_penyewa=penyewa.id_penyewa, 
                             tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai, 
                             total_pembayaran=jumlah_bayar)
        db.session.add(transaksi)
        db.session.commit()

         # Update status kontrakan menjadi 'Disewa'
        kontrakan = Kontrakan.query.get(id_kontrakan)
        if kontrakan:
            kontrakan.status = 'Disewa'
            db.session.commit()

        # Simpan data pembayaran
        pembayaran = Pembayaran(id_transaksi=transaksi.id_transaksi, tanggal_bayar=date.today(), 
                                jumlah_bayar=jumlah_bayar)
        db.session.add(pembayaran)
        db.session.commit()

        return redirect('/success')

    return render_template('pesan.html', kontrakan=kontrakan)


@app.route('/success')
def success():
    return "<h1>Pemesanan berhasil! Terima kasih.</h1>"


if __name__ == '__main__':
    app.run(debug=True)
