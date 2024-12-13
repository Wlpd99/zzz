from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    _tablename_ = 'users'  # Menentukan nama tabel di database
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
class Kontrakan(db.Model):
    __tablename__ = 'kontrakan'
    id_kontrakan = db.Column(db.Integer, primary_key=True)
    alamat = db.Column(db.String(255), nullable=False)
    fasilitas = db.Column(db.Text, nullable=True)
    harga_per_bulan = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('Tersedia', 'Disewa', name='status_kontrakan_enum'), 
                       default='Tersedia', nullable=False)                

    def __repr__(self):
        return f'<Kontrakan id={self.id_kontrakan} alamat={self.alamat} status={self.status}>'

class Penyewa(db.Model):
    __tablename__ = 'penyewa'
    id_penyewa = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    no_telepon = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    alamat = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Penyewa id={self.id_penyewa} nama={self.nama}>'

class Transaksi(db.Model):
    __tablename__ = 'transaksi'
    id_transaksi = db.Column(db.Integer, primary_key=True)
    id_kontrakan = db.Column(db.Integer, db.ForeignKey('kontrakan.id_kontrakan'), nullable=False)
    id_penyewa = db.Column(db.Integer, db.ForeignKey('penyewa.id_penyewa'), nullable=False)
    tanggal_mulai = db.Column(db.Date, nullable=False)
    tanggal_selesai = db.Column(db.Date, nullable=True)
    total_pembayaran = db.Column(db.Numeric(10, 2), nullable=True)

    kontrakan = db.relationship('Kontrakan', backref=db.backref('transaksi', lazy='dynamic', cascade='all, delete'))
    penyewa = db.relationship('Penyewa', backref=db.backref('transaksi', lazy='dynamic', cascade='all, delete'))

    def __repr__(self):
        return f'<Transaksi id={self.id_transaksi} id_kontrakan={self.id_kontrakan} id_penyewa={self.id_penyewa}>'

class Pembayaran(db.Model):
    __tablename__ = 'pembayaran'
    id_pembayaran = db.Column(db.Integer, primary_key=True)
    id_transaksi = db.Column(db.Integer, db.ForeignKey('transaksi.id_transaksi'), nullable=False)
    tanggal_bayar = db.Column(db.Date, nullable=False)
    jumlah_bayar = db.Column(db.Numeric(10, 2), nullable=False)

    transaksi = db.relationship('Transaksi', backref=db.backref('pembayaran', lazy='dynamic', cascade='all, delete'))

    def __repr__(self):
        return f'<Pembayaran id={self.id_pembayaran} id_transaksi={self.id_transaksi}>'
