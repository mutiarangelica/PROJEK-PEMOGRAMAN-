import streamlit as st
import json, sqlite3, csv, io
from datetime import datetime
from core import BASE,SUBBAB,TUGAS,RUBRIK,db,init,register,login,search,password
import secrets
st.set_page_config(page_title='Ruang Biografi',page_icon='📚',layout='wide')
init()
st.markdown('''<style>.stApp{background:#f7f8fc}h1,h2,h3{color:#29365c}.stButton>button{border-radius:12px}section[data-testid="stSidebar"]{background:#eaf0fa}</style>''',unsafe_allow_html=True)
st.title('📚 Ruang Biografi')
st.caption('Baca kisahnya • Uji pemahamanmu • Tulis dengan bukti')
if 'user' not in st.session_state:
 st.info('Masuk untuk menyimpan materi dan pekerjaanmu.')
 with db() as c: has_teacher=bool(c.execute("SELECT 1 FROM users WHERE role='Guru'").fetchone())
 a,b=st.tabs(['Masuk','Daftar'])
 with a:
  with st.form('login'):
   u=st.text_input('Nama pengguna');p=st.text_input('Kata sandi',type='password');role=st.selectbox('Masuk sebagai',['Mahasiswa','Guru'])
   if st.form_submit_button('Masuk',use_container_width=True):
    user=login(u,p)
    if user and user['role']==role:
     st.session_state.user={k:user[k] for k in ('id','username','name','role')};st.rerun()
    else:st.error('Nama pengguna, kata sandi, atau peran tidak sesuai.')
 with b:
  if not has_teacher:st.warning('Pengajar: buat akun guru pertama sebelum membagikan aplikasi kepada mahasiswa.')
  with st.form('register'):
   n=st.text_input('Nama lengkap');u=st.text_input('Nama pengguna baru');p=st.text_input('Kata sandi baru',type='password');p2=st.text_input('Ulangi kata sandi',type='password')
   r=st.selectbox('Peran',['Mahasiswa'] if has_teacher else ['Mahasiswa','Guru'])
   if st.form_submit_button('Buat akun'):
    try:
     if p!=p2:raise ValueError('Kata sandi tidak sama.')
     register(u,n,p,r);st.success('Akun tersimpan. Silakan masuk.');st.rerun()
    except (ValueError,sqlite3.IntegrityError) as e:st.error('Nama pengguna sudah digunakan.' if isinstance(e,sqlite3.IntegrityError) else str(e))
 st.stop()
user=st.session_state.user;teacher=user['role']=='Guru'
with st.sidebar:
 st.subheader(user['name']);st.caption(user['role'])
 menu=st.radio('Menu',['Beranda','Materi Biografi','Materi Tersimpan','LKPD','Tutor Materi','Modul Guru','Dashboard Guru'] if teacher else ['Beranda','Materi Biografi','Materi Tersimpan','LKPD','Tutor Materi'])
 if st.button('Keluar'):st.session_state.clear();st.rerun()
with db() as c: materials=[dict(x) for x in c.execute('SELECT * FROM materials ORDER BY rowid')]
if menu=='Beranda':
 st.header('Belajar dari perjalanan hidup tokoh')
 st.write('Pelajari materi, baca biografi pilihan pengajar, kemudian kerjakan empat LKPD secara bertahap.')
 cols=st.columns(3)
 cols[0].metric('Subbab',len(materials));cols[1].metric('Materi tersedia',sum(bool(x['body'].strip()) for x in materials))
 with db() as c:count=c.execute("SELECT COUNT(*) FROM submissions WHERE user_id=? AND status='Dikirim'",(user['id'],)).fetchone()[0]
 cols[2].metric('LKPD dikirim',count)
 st.subheader('Tujuan pembelajaran — rancangan yang dapat disesuaikan')
 st.write('Mahasiswa mampu mengidentifikasi informasi dan struktur biografi, menganalisis penggunaan bahasa serta bukti, menilai keteladanan secara kritis, dan menulis biografi dengan sumber yang jelas.')
 st.info('Mulai dari Materi Biografi, lalu LKPD. Materi kosong akan diisi pengajar; tujuan di atas belum merupakan capaian resmi mata kuliah.')
elif menu in ('Materi Biografi','Materi Tersimpan'):
 if menu=='Materi Tersimpan':
  with db() as c:saved={r[0] for r in c.execute('SELECT title FROM bookmarks WHERE user_id=?',(user['id'],))}
  materials=[x for x in materials if x['title'] in saved]
 if not materials:st.info('Belum ada materi yang ditandai untuk dipelajari kembali.')
 else:
  title=st.selectbox('Pilih subbab',[x['title'] for x in materials]);m=next(x for x in materials if x['title']==title)
  st.header(title)
  if m['body']:st.markdown(m['body']);st.caption('Sumber: '+(m['source'] or 'Belum dicantumkan'))
  else:st.info('Materi belum ditambahkan oleh pengajar.')
  with db() as c:marked=bool(c.execute('SELECT 1 FROM bookmarks WHERE user_id=? AND title=?',(user['id'],title)).fetchone())
  if st.button('Hapus dari simpanan' if marked else '🔖 Simpan materi'):
   with db() as c:
    if marked:c.execute('DELETE FROM bookmarks WHERE user_id=? AND title=?',(user['id'],title))
    else:c.execute('INSERT OR IGNORE INTO bookmarks VALUES(?,?)',(user['id'],title))
   st.rerun()
  if m['body']:st.download_button('Unduh materi TXT',m['body']+'\n\nSumber: '+m['source'],file_name='materi_biografi.txt')
  if teacher:
   with st.expander('✏️ Tambah / edit materi'):
    with st.form('edit_material'):
     body=st.text_area('Isi materi (boleh Markdown)',m['body'],height=300);src=st.text_input('Sumber / referensi',m['source']);upload=st.file_uploader('Atau impor TXT UTF-8',type=['txt'])
     if st.form_submit_button('Simpan perubahan'):
      try:
       if upload:body=upload.getvalue().decode('utf-8-sig')
       with db() as c:c.execute('UPDATE materials SET body=?,source=? WHERE title=?',(body,src,title))
       st.rerun()
      except UnicodeDecodeError:st.error('Simpan berkas dalam encoding UTF-8 terlebih dahulu.')
elif menu=='LKPD':
 st.header('Lembar Kerja Mahasiswa')
 st.write('Gunakan biografi dan sumber yang ditetapkan pengajar. Simpan draf sebelum keluar; kirim setelah jawaban lengkap.')
 task=st.selectbox('Pilih kegiatan',list(TUGAS))
 with db() as c:row=c.execute('SELECT * FROM submissions WHERE user_id=? AND task=?',(user['id'],task)).fetchone()
 answers=json.loads(row['answers']) if row else {}
 if row:
  st.caption('Status: '+row['status']+' • Terakhir disimpan: '+row['updated'])
  if row['score'] is not None:st.success(f"Nilai: {row['score']}/100");st.write('Umpan balik guru: '+row['feedback'])
 with st.expander('Rubrik penilaian'):
  for k,v in RUBRIK.items():st.write(f'{k}: maksimal {v} poin')
 locked=bool(row and row['status']=='Dikirim')
 with st.form('answers_'+task):
  values={str(i):st.text_area(f'{i+1}. {q}',answers.get(str(i),''),height=140,disabled=locked) for i,q in enumerate(TUGAS[task])}
  draft=st.form_submit_button('Simpan draf',disabled=locked);send=st.form_submit_button('Kirim ke guru',disabled=locked)
  if draft or send:
   if send and any(not v.strip() for v in values.values()):st.error('Lengkapi semua jawaban sebelum mengirim.')
   else:
    with db() as c:c.execute('INSERT INTO submissions(user_id,task,answers,status,updated) VALUES(?,?,?,?,?) ON CONFLICT(user_id,task) DO UPDATE SET answers=excluded.answers,status=excluded.status,updated=excluded.updated,score=NULL,feedback=\'\'',(user['id'],task,json.dumps(values,ensure_ascii=False),'Dikirim' if send else 'Draf',datetime.now().isoformat(timespec='seconds')))
    st.rerun()
 if locked:st.info('Jawaban sudah dikirim. Guru dapat membukanya kembali untuk revisi.')
elif menu=='Tutor Materi':
 st.header('💬 Tutor berbasis materi')
 st.caption('Mode pencarian lokal: menampilkan kutipan relevan, belum menggunakan AI generatif atau API.')
 docs=[(x['title'],x['body'],x['source']) for x in materials if x['body'].strip()]
 for f in sorted((BASE/'database').glob('*.txt')):
  try:docs.append((f.stem.replace('_',' '),f.read_text(encoding='utf-8-sig'),f.name))
  except UnicodeError:st.warning(f'Berkas {f.name} bukan UTF-8.')
 with st.form('tutor'):
  q=st.text_input('Pertanyaanmu',placeholder='Apa struktur biografi?')
  if st.form_submit_button('Cari penjelasan'):
   if not q.strip():st.warning('Isi pertanyaan terlebih dahulu.')
   elif not docs:st.info('Materi belum tersedia. Pengajar perlu menambahkan materi atau TXT terlebih dahulu.')
   else:
    result=search(q,docs)
    if not result:st.warning('Belum ditemukan kutipan yang sesuai. Coba pertanyaan lebih spesifik atau minta pengajar melengkapi materi.')
    for _,title,p,src in result:
     st.subheader(title);st.write(p);st.caption('Sumber: '+(src or 'Referensi belum dicantumkan'))
 st.info('Petunjuk LKPD: gunakan bukti dari teks, jelaskan alasanmu, lalu periksa apakah kesimpulanmu didukung sumber.')
elif menu=='Modul Guru' and teacher:
 st.header('Modul pembelajaran pengajar')
 with db() as c:row=c.execute("SELECT value FROM settings WHERE key='modul'").fetchone()
 default='''# Modul Pembelajaran Biografi

## Identitas
Mata kuliah: [isi]\nSemester: [isi]\nAlokasi waktu: [isi]

## Capaian pembelajaran
[Isi CPL/CPMK resmi dari dokumen mata kuliah.]

## Tujuan
Mengidentifikasi informasi dan struktur; menganalisis bahasa dan bukti; menilai keteladanan; menulis biografi bersumber.

## Persiapan
Tentukan teks biografi, sumber, dan kebutuhan mahasiswa. Lengkapi materi setiap subbab.

## Kegiatan awal
Diskusikan tokoh pilihan dan pengetahuan awal mahasiswa.

## Kegiatan inti
LKPD 1: informasi tokoh.\nLKPD 2: struktur dan bahasa.\nLKPD 3: pembacaan kritis.\nLKPD 4: penulisan dan revisi.

## Penutup
Refleksi kesulitan, umpan balik pengajar, dan tindak lanjut revisi.

## Asesmen
Isi dan bukti 35; struktur 25; penalaran 25; bahasa dan sumber 15. Nilai ditetapkan pengajar berdasarkan kualitas jawaban.

## Referensi
[Tambahkan referensi yang benar-benar digunakan.]
'''
 content=row[0] if row else default
 with st.form('modul'):
  updated=st.text_area('Edit modul (Markdown)',content,height=450)
  if st.form_submit_button('Simpan modul'):
   with db() as c:c.execute("INSERT INTO settings VALUES('modul',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(updated,))
   st.rerun()
 st.download_button('Unduh modul',content,file_name='modul_guru_biografi.md');st.markdown(content)
elif menu=='Dashboard Guru' and teacher:
 st.header('Dashboard Guru')
 with db() as c:
  students=[dict(r) for r in c.execute("SELECT id,name,username FROM users WHERE role='Mahasiswa'")]
  rows=[dict(r) for r in c.execute("SELECT s.*,u.name,u.username FROM submissions s JOIN users u ON s.user_id=u.id WHERE u.role='Mahasiswa' ORDER BY s.updated DESC")]
 st.metric('Akun mahasiswa',len(students))
 if students:st.dataframe(students,hide_index=True,use_container_width=True)
 if not rows:st.info('Belum ada jawaban mahasiswa.')
 else:
  st.dataframe([{k:r[k] for k in ('name','username','task','status','updated','score')} for r in rows],hide_index=True,use_container_width=True)
  out=io.StringIO();fields=['name','username','task','status','updated','score','feedback','answers'];w=csv.DictWriter(out,fieldnames=fields);w.writeheader()
  for r in rows:
   clean={k:r[k] for k in fields}
   for k,v in clean.items():
    if isinstance(v,str) and v.startswith(('=','+','-','@')):clean[k]="'"+v
   w.writerow(clean)
  st.download_button('Unduh rekap CSV',out.getvalue().encode('utf-8-sig'),file_name='rekap_lkpd.csv')
  idx=st.selectbox('Periksa pekerjaan',range(len(rows)),format_func=lambda i:f"{rows[i]['name']} (@{rows[i]['username']}) — {rows[i]['task']} — {rows[i]['status']}")
  r=rows[idx]
  for i,q in enumerate(TUGAS[r['task']]):st.markdown(f'**{i+1}. {q}**');st.write(json.loads(r['answers']).get(str(i),''))
  if r['status']=='Dikirim':
   with st.form('grade_'+str(r['user_id'])+r['task']):
    marks=[st.number_input(k,min_value=0,max_value=v,value=0,key=f"{r['user_id']}_{r['task']}_{k}") for k,v in RUBRIK.items()]
    st.caption('Isi seluruh komponen untuk memberi atau mengganti nilai.');feedback=st.text_area('Umpan balik guru',r['feedback'])
    if st.form_submit_button('Simpan nilai'):
     with db() as c:c.execute('UPDATE submissions SET score=?,feedback=? WHERE user_id=? AND task=?',(sum(marks),feedback,r['user_id'],r['task']))
     st.rerun()
   if st.button('Buka kembali untuk revisi'):
    with db() as c:c.execute("UPDATE submissions SET status='Draf',score=NULL,feedback='' WHERE user_id=? AND task=?",(r['user_id'],r['task']))
    st.rerun()
 with st.expander('Tambahkan pengajar lain'):
  with st.form('extra_teacher'):
   name=st.text_input('Nama pengajar');username=st.text_input('Username pengajar');pw=st.text_input('Password pengajar',type='password')
   if st.form_submit_button('Buat akun guru'):
    try:
     import re
     if not name.strip() or not re.fullmatch(r'[a-z0-9_.-]{3,40}',username) or len(pw)<8:raise ValueError('Isi nama, username valid (3–40 karakter), dan password minimal 8 karakter.')
     salt=secrets.token_hex(16)
     with db() as c:c.execute('INSERT INTO users(username,name,role,salt,hash) VALUES(?,?,?,?,?)',(username,name.strip(),'Guru',salt,password(pw,salt)))
     st.success('Akun guru dibuat.')
    except (ValueError,sqlite3.IntegrityError) as e:st.error(str(e))
