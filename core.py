import sqlite3, hashlib, secrets, hmac, re, math
from pathlib import Path
BASE = Path(__file__).resolve().parent
SUBBAB = ['Pengertian Biografi','Tujuan dan Manfaat','Ciri-ciri Biografi','Struktur Biografi','Kaidah Kebahasaan','Contoh dan Analisis','Langkah Menulis Biografi']
TUGAS = {
 'LKPD 1 — Mengenali tokoh': ['Tuliskan judul dan sumber biografi yang kamu baca.','Siapa tokohnya dan apa bidang kontribusinya?','Catat lima informasi penting beserta bukti dari teks.'],
 'LKPD 2 — Struktur dan bahasa': ['Salin bagian orientasi dan jelaskan alasanmu.','Jelaskan urutan peristiwa penting beserta bukti teks.','Apakah ada reorientasi? Jelaskan dengan bukti.','Temukan contoh kata kerja, penanda waktu, dan kata rujukan; jelaskan fungsinya.'],
 'LKPD 3 — Membaca kritis': ['Apa nilai keteladanan tokoh? Sertakan bukti.','Pernyataan mana yang berupa fakta dan mana yang berupa penilaian penulis?','Informasi apa yang perlu diverifikasi melalui sumber lain?'],
 'LKPD 4 — Menulis biografi': ['Tuliskan tokoh, alasan pemilihan, dan sumber informasi.','Susun kerangka orientasi, peristiwa penting, dan penutup.','Tuliskan biografi berdasarkan sumber yang dapat diperiksa.','Jelaskan revisi yang kamu lakukan dan refleksi belajarmu.']}
RUBRIK = {'Ketepatan isi dan bukti':35,'Kelengkapan dan struktur':25,'Analisis dan penalaran':25,'Bahasa dan sumber':15}
def db():
 c=sqlite3.connect(BASE/'data.sqlite3',timeout=20); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c

def init():
 with db() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, name TEXT, role TEXT, salt TEXT, hash TEXT);
CREATE TABLE IF NOT EXISTS materials(title TEXT PRIMARY KEY, body TEXT DEFAULT '', source TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS bookmarks(user_id INTEGER REFERENCES users(id),title TEXT REFERENCES materials(title),PRIMARY KEY(user_id,title));
CREATE TABLE IF NOT EXISTS submissions(user_id INTEGER REFERENCES users(id),task TEXT,answers TEXT,status TEXT,updated TEXT,score REAL,feedback TEXT DEFAULT '',PRIMARY KEY(user_id,task));
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);''')
  c.executemany('INSERT OR IGNORE INTO materials(title) VALUES(?)',[(x,) for x in SUBBAB])

def password(p,s): return hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),200000).hex()
def register(username,name,p,role):
 username=username.strip().lower()
 if not re.fullmatch(r'[a-z0-9_.-]{3,40}',username): raise ValueError('Nama pengguna: 3–40 huruf, angka, titik, garis bawah, atau tanda minus.')
 if not name.strip() or len(p)<8: raise ValueError('Isi nama dan gunakan kata sandi minimal 8 karakter.')
 if role not in ('Mahasiswa','Guru'): raise ValueError('Peran tidak valid.')
 salt=secrets.token_hex(16)
 with db() as c:
  if role=='Guru' and c.execute("SELECT 1 FROM users WHERE role='Guru'").fetchone(): raise ValueError('Akun guru sudah tersedia. Tambahan guru dibuat oleh guru yang masuk.')
  c.execute('INSERT INTO users(username,name,role,salt,hash) VALUES(?,?,?,?,?)',(username,name.strip(),role,salt,password(p,salt)))
def login(u,p):
 with db() as c: row=c.execute('SELECT * FROM users WHERE username=?',(u.strip().lower(),)).fetchone()
 return dict(row) if row and hmac.compare_digest(row['hash'],password(p,row['salt'])) else None
STOP=set('apa itu adalah yang dan di ke dari pada dengan untuk dalam bagaimana jelaskan tentang saya sebuah'.split())
def tokens(t): return [x for x in re.findall(r'\w+',t.lower()) if len(x)>2 and x not in STOP]
def search(q,docs):
 query=set(tokens(q)); intent=set(query)-{'biografi','teks','materi','tokoh'}
 if not query:return []
 chunks=[]
 for title,body,source in docs:
  for p in re.split(r'\n\s*\n',body):
   if p.strip():
    for start in range(0,len(p),1800): chunks.append((title,p[start:start+2000],source))
 ranked=[]
 for title,p,src in chunks:
  words=tokens(p); wt=set(words); tt=set(tokens(title)); overlap=query & (wt|tt)
  if not overlap or (intent and not intent & (wt|tt)):continue
  score=sum((1+math.log(1+words.count(w)))*(1+math.log((len(chunks)+1)/(1+sum(w in set(tokens(b)) for _,b,_ in chunks)))) for w in overlap)+3*len(query&tt)
  ranked.append((score,title,p,src))
 return sorted(ranked,reverse=True)[:3]
