face-recognition 1.0

Beberapa hal di README ini mungkin akan berubah, untuk info lebih lengkap hubungi author
Tata cara menjalankan
    ada baiknya baca seluruh manual ini sampai selesai terlebih dahulu, sampai anda paham.
    tambahkan foto pada folder new_images lalu run multi_encode.py
    jalankan data_adder.py tambahkan data murid. Penjelasan lebih lengkap, di bawah
    
    MANUAL ->
    jalankan run.py
    jangan lupa ubah .env untuk mengubah jam masuk sekolah
    jika gerbang telah tertutup atau dirasa telah cukup maka hentikan program dengan tombol Q
    ## tidak tersedia lagi-> lalu jalankan absensi.py untuk merekap siswa yang tidak masuk dan telat

Tata cara install
    pada linux system jangan lupa lakukan 
        sudo apt-get install -y build-essential
        sudo apt-get install python3-dev
        sudo apt install cmake
        atau menggunakan boostrap_linux.sh
        dengan cara memberi izin execution pada file tersebut lalu run di terminal anda
        dengan cara klik kanan lalu open in terminal dan ketik ./boostrap_linux.sh
    Pastikan CMake telah terinstall
    Jika ingin menggunakan venv ->> py -m venv venv
        ./venv/Scripts/activate
    Atau jika tidak ingin memakai venv langsung saja run pip
    run pip install -r ./requirements.txt

Ubah jadwal jam masuk terakhir di file .env dengan format "JJ:MM:DD" Jam Menit Detik

Jika ingin menambahkan foto, tempatkan foto di dalam folder new_images
Setelah itu run multi_encode.py
    Mode refresh adalah bin yang tersedia dihapus setelah itu memindahkan semua foto dari folder
    images ke new_images untuk di proses ulang, jika terjadi kesalahan dalam foto siswa atau ada siswa baru
    jika misal ada siswa yang keluar atau pindah sekolah anda bisa saja menghapus foto siswa tersebut lalu
    menjalankan multi_encode.py dalam mode refresh bin untuk menghapus siswa tersebut, database tidak berubah.
    Pastikan id pada foto tidak terduplikat contohnya ada foto dengan id 112233 nah filenya
    112233.png namun ada juga 112233.jpg ini dapat mengganggu pengenalan wajah apalagi jika kedua foto tersebut
    beda orang.

Tambahkan data murid ke database dengan menjalankan data_adder.py
    Anda bisa memilih mode manual / dari excel
    Pastikan agar id gambar tidak terduplikat
    id yang telah dipakai tidak boleh dipakai lagi
    Id harus sesuai dengan nama foto nya contoh
        12345.jpg
        maka idnya adalah 12345
    Jika ingin mengedit nama siswa, masukkan id siswa sebelumnya lalu masukkan nama baru dan data selanjutnya.
    Saya sarankan agar tidak mengubah id siswa karena id siswa dipakai juga untuk menyimpan tanggal masuk, waktu
    telat

    AUTO ->
        kolom id pada excel harus ber tipe teks jangan angka, karena angka 000 didepan akan hilang sendiri
        contoh anda memasukkan id 0012356 maka di excel akan tertulis 12356 tanpa 00 didepan
        tempatkan template.xlsx pada folder db
        lalu jalankan data_adder.py dengan mode A atau a untuk mode auto
        anda bisa mengedit data nama / kelas pada id target secara langsung, misal sebelumnya id 00123 adalah kelas 5, maka di excel anda hanya perlu mengubah kelas pada id target menjadi 6 misalkan.

Tampilan
    Icon centang - terabsen (tidak akan duplikat pada hari yang sama) ABSEN TIDAK AKAN TERDUPLIKAT
        Misal ada si Jojo telah terabsen dan tercentang, lalu ada si Jotaro. Nah jika Jojo tidak sengaja
        tercentang lagi, ini aman. Karena walau sudah tercentang tidak akan terkirim lagi ke database.
    Icon info - sudah terabsen (tidak perlu mengulang lagi)
    None in database - jika nama siswa muncul sebagai None in database maka belum ditambahkan di database

Debug info : 
db.py :
    Downloading data from database - Mendownload ke cache lokal dari database
    Attendance marked - Absensi diterima lalu mengupdate yang ada di database
    Already marked - di database sudah terdeteksi namun cache lokal belum update, biasanya program ke restart
    ID not found in database - id wajah yang dikenali tidak terdapat di database, tambahkan informasi siswa
    tersebut
student.py :
    No binary found - anda belum menjalankan multi_encode.py yang menghasilkan file known_faces_encodings.pkl
        di folder bin. Jika menjalankan program tanpa bin maka wajah tidak akan dikenali
    Images are not compatible with total of encodings - total encoding lebih banyak daripada foto yang tersedia
        yang mengakibatkan index out of bound atau tidak menemukan foto yang sesuai. Wajah bisa saja salah.
        biasanya ada foto yang terhapus di folder images.
    Encodings not enough - foto yang tersedia melebihi encodings yang ada, yang berakibat wajah salah nama.
multi_encode.py :
    Using non multiprocess - file ini tidak dijalankan secara langsung melainkan dari file lainnya.
    Found folders - pastikan tidak ada folder di dalam folder new_images
lazy_attend.py :
    Listening - menunggu siswa untuk absen, dan jika tidak ditemukan file di post_periodic

Cara kerja cache :
    pertama kali run maka akan mendownload data dari database ke cache local, jika aplikasi terkena restart dalam
    waktu 10 menit maka akan mendownload data baru. Jika terdeteksi ada penambahan data di database seperti
    menambah data siswa maka flag sync_status akan berubah ke false di database. Hal ini dapat terjadi melalui
    data_adder.py ketika ingin mengedit atau menambah data siswa.

Cara kerja post periodic :
    file yang akan di post adalah file pada hari itu juga, nah karena hal ini maka pada hari minggu lazy_attend.py tidak akan berjalan jika terjadi uji coba run.py pada hari minggu. Jika ditemukan file berumur lebih dari 3
    hari maka akan di hapus. Siswa yang telah di post maka id nya akan di simpan juga di post.checkpoint agar
    tidak terupload lagi.

CRON JOB :
    @reboot cd /path/to/face-recognition;XDG_RUNTIME_DIR=/run/user/$(id -u) /path/to/face-recognition/run.sh

    Jika tidak stabil maka tambahkan sleep 80; sebelum cd seperti : 
    @reboot sleep 80;cd /path/to/face-recognition;
    eksperimen lah pada waktu sleep karena setiap komputer dapat berbeda tergantung kemampuan hardware nya
    
    */5 * * * 1-6 cd path/to/face-recognition && path/to/face-recognition/lazy_attend.py

    for debug purpose : 
    This will log all stdout and stderr
    */5 * * * 1-6 cd path/to/face-recognition && path/to/face-recognition/lazy_attend.py >> path/to/logs/log.txt 2>&1
        contohnya : 
        @reboot sleep 80;cd /home/zeef/face-recognition;XDG_RUNTIME_DIR=/run/user/$(id -u) /home/zeef/face-recognition/run.sh >> /home/zeef/face-recognition/logs/logs_cron.txt 2>&1

Team developer Nusantara Sinergi
Pimpinan
    ~ Bapak zefri
Programmer
    ~ Bapak zainullah
    ~ Hudman H.A.
      Instagram : @less_extreme
