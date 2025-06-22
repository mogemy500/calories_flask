from flask import Flask, render_template, request, redirect, url_for, flash,session
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "any_secret_key"
import sqlite3
from datetime import datetime
import re
import os
from flask import send_from_directory
def init_db():
    with sqlite3.connect('guestbooks.db') as conn:
        
         cur = conn.cursor()
         cur.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
             created_at TEXT NOT NULL
            
        )
    ''')
         cur.execute('''
        CREATE TABLE IF NOT EXISTS sign (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
            )
    ''') 
         cur.execute('''
        CREATE TABLE IF NOT EXISTS calories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            Weight int NOT NULL,
            height int NOT NULL,
            age int NOT NULL,
            kind text NOT NULL,
            result REAL NOT NULL
            
        )
        
        
    ''')
         cur.execute('''
         CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        login_time TEXT NOT NULL
    )
''')


         cur.execute('''
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        uploaded_at TEXT NOT NULL
    )
''')

         conn.commit()
        

# نشغّل الدالة مرة واحدة عند بداية البرنامج
init_db()

@app.route('/', methods=['GET', 'POST'])    
def sign():
    commn_lsit=["123456","password","qwerty","abc123","123132","111111","letmin"]
    sympols="!#@"
     
    conn = sqlite3.connect('guestbooks.db')
    cur = conn.cursor()
    
     
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password =request.form['password']
        has_upper = any(c.isupper() for c in password)    
        has_lower = any(c.islower() for c in password)
        
        if not name or not password or not email :
            flash('من فضلك املأ جميع الحقول.')
        elif len(password) < 8 :
            flash('من فضلك الرقم السري لا يقل عن 8 حروف')
        elif password.lower() in commn_lsit:
            flash('هذه الكلمات محجوزه')
        elif not  password[0].isupper():
            flash('يجب ان يبدا الرقم السري بحرف كببير')
        
        
        
       
        elif not( has_upper and has_lower):
            flash('يجب ان يحتوي الرقم السري علي حروف صفيره وكبيره')
       
        elif not  any(c.isdigit()  for c in password):
            flash('يجب ان يكون الرقم السري به ارقام')
         
        elif not  any(c in sympols  for c in password):
            flash('يجب ان يحتوي علي بعض الرموز !#@')
        elif not password.strip():
            flash('لا يسمح بالرفاغات بين الرقم السري.')
        #elif not  name[0].isupper():
          #  flash('يجب الاسن ان يبداء بحرف كبير.')
        elif not  name[1:].islower():
            flash('يكب ان تكون باقي الحروف صغيثره بعد الحرف الاول.')
        elif not name.strip():
            flash('لا يسمح بالفراغات بين الاسم.')
        elif not  name.isalpha():
            flash('يجب لاسم ان يحتوي علي حروف فقط.')
        elif not re.match(r'^[ء-يa-zA-Z]+$', name):
            flash('الاسم يجب أن يحتوي على حروف عربية أو إنجليزية فقط.')  
        elif not email.strip():  
           flash('لايسمج بالفراغات.')
        elif  email.startswith("@") or email.startswith("."):  
           flash('لايجب ان يحتوي علي علي هذه العلامات في بدايه الايميل.')
        elif "@" not in  email:
           flash('يجب ان يحتوي علي @.') 
        elif "." not in  email.split("@")[-1]:
           flash('يجب ان يحتوي علي ".".') 
        else:
            cur.execute("INSERT INTO sign (name, email,password) VALUES (?, ?,?)", (name, email,password))
            conn.commit()
            flash('تم الحساب بنجاح!')
            return redirect(url_for('login'))
    return render_template('sign.html',)    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = sqlite3.connect('guestbooks.db')
    cur = conn.cursor()
    if request.method == 'POST':
        email = request.form['email']
        password=request.form['password']
        login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(f"select * from sign where email =? and password =?",(email, password))
        results = cur.fetchall()
        if  results:
            session['user'] = email
            flash('تم تسجيل الدخول بنجاح!')
            
            cur.execute("INSERT INTO logins (email, login_time) VALUES (?, ?)", (email, login_time))
            conn.commit()

            return redirect(url_for('dashboard'))
        else:
            flash('يرجي تسجيل حساب!')
            return redirect(url_for('sign'))
    return render_template('login.html',)


@app.route('/calories', methods=['GET', 'POST'])
def calories():
    if 'user' not in session:
       flash('يجب تسجيل الدخول أولًا.')
       return redirect(url_for('login'))

    result = None 
    if request.method == 'POST':
        Weight = float(request.form['Weight'])
        height = float(request.form['height'])
        age = float(request.form['age'])
        kind=request.form['kind']
        email = session.get('user')
        if kind =="male":
            result=Weight * 10 +  height * 6.25 - age * 5 + 5
        if kind =="female":
            result= Weight * 10 + height * 6.25 - age * 5 -161
        
        conn = sqlite3.connect('guestbooks.db')
        cur = conn.cursor()
       
        
        cur.execute("INSERT INTO calories (email,Weight, height,age,kind,result) VALUES (?,?, ?,?,?,?)", (email,Weight, height,age,kind,result))
        conn.commit()

        session['result'] = result

        # ❌ ما تطبعش النتيجة فورًا
        return redirect(url_for('calories'))

    # عرض النتيجة بعد redirect
    result = session.pop('result', None)
    return render_template('calories.html', result=result)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("تم تسجيل الخروج.")
    return redirect(url_for('login'))
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("يجب تسجيل الدخول أولاً.")
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')
@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if 'user' not in session:
        flash('يجب تسجيل الدخول أولًا.')
        return redirect(url_for('login'))    
    email = session.get('user')
    conn = sqlite3.connect('guestbooks.db')
    cur = conn.cursor()

    cur.execute("SELECT name FROM sign WHERE email = ?", (email,))
    user = cur.fetchone()
 
    if not user:
        flash('حدث خطأ. يرجى تسجيل الدخول مرة أخرى.')
        conn.close()
        return redirect(url_for('login'))
    name = user[0]
    if request.method == 'POST':
        message = request.form['message']
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
        if not message.strip():
            flash("لا يمكن إرسال رسالة فارغة.")
        
 
        
        else:
            
            cur.execute("INSERT INTO guests (name, message,email, created_at) VALUES (?, ?, ?,?)",(name, message, email,created_at))
            conn.commit()
            flash('تم إرسال الرسالة بنجاح!')
            
        conn.close()
        return redirect(url_for('dashboard'))
    conn.close()
    return render_template('comment.html' )

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        flash("يجب تسجيل الدخول أولًا")
        return redirect(url_for('login'))

    email = session['user']

    conn = sqlite3.connect('guestbooks.db')
    cur = conn.cursor()

    if request.method == 'POST':
        new_name = request.form['name']
        new_password = request.form['password']

        cur.execute("UPDATE sign SET name = ?, password = ? WHERE email = ?", 
                    (new_name, new_password, email))
        conn.commit()
        conn.close()
        flash('تم تحديث البيانات بنجاح')
        return redirect(url_for('dashboard'))

    cur.execute("SELECT name, email, password FROM sign WHERE email = ?", (email,))
    user_data = cur.fetchone()
    conn.close()
    return render_template('edit_profile.html', user_data=user_data)

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'user' not in session:
        flash("يجب تسجيل الدخول أولًا")
        return redirect(url_for('login'))

    email = session['user']

    conn = sqlite3.connect('guestbooks.db')
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("DELETE FROM sign WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        session.pop('user', None)
        flash('تم حذف الحساب.')
        return redirect(url_for('sign'))

    return render_template('confirm_delete.html')


@app.route('/delete_calories', methods=['GET', 'POST'])
def delete_calories():
    if 'user' not in session:
        flash("يجب تسجيل الدخول أولًا.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        email = session['user']
        conn = sqlite3.connect('guestbooks.db')
        cur = conn.cursor()

        cur.execute("DELETE FROM calories WHERE email = ?", (email,))
        conn.commit()
        conn.close()

        flash("تم حذف بيانات السعرات الحرارية.")
        return redirect(url_for('dashboard'))
    return render_template('confirm_delete_calories.html')

@app.route('/edit_calories', methods=['GET', 'POST'])
def edit_calories():
    if 'user' not in session:
        flash("يجب تسجيل الدخول أولًا.")
        return redirect(url_for('login'))

    email = session['user']
    conn = sqlite3.connect('guestbooks.db')
    cur = conn.cursor()

    if request.method == 'POST':
        # بيانات جديدة فقط من النموذج
        Weight = float(request.form['Weight'])
        height = float(request.form['height'])
        age = float(request.form['age'])
        kind = request.form['kind']

        if kind == "male":
            result = Weight * 10 + height * 6.25 - age * 5 + 5
        else:
            result = Weight * 10 + height * 6.25 - age * 5 - 161

        # تعديل آخر سجل بناءً على الإيميل
        cur.execute('''
            UPDATE calories
            SET Weight = ?, height = ?, age = ?, kind = ?, result = ?
            WHERE email = ?
        ''', (Weight, height, age, kind, result, email))

        conn.commit()
        flash('تم تعديل بيانات السعرات بنجاح.')
        return redirect(url_for('dashboard'))
    cur.execute("SELECT Weight, height, age, kind FROM calories WHERE email = ? ORDER BY id DESC LIMIT 1", (email,))
    user_data = cur.fetchone()

    conn.close()
    return render_template('edit_calories.html', user_data=user_data)


@app.route('/show',)
def show():
    if 'user' not in session:
        flash("يجب تسجيل الدخول أولًا.")
        return redirect(url_for('login'))

    email = session['user']
    conn = sqlite3.connect('guestbooks.db')
    cur = conn.cursor()

    # استعلام يضم بيانات المستخدم مع السعرات الحرارية
    cur.execute('''
        SELECT sign.name, sign.email, sign.password, 
               calories.Weight, calories.height, calories.age, 
               calories.kind, calories.result
        FROM sign
        LEFT JOIN calories ON sign.email = calories.email
        WHERE sign.email = ?
    ''', (email,))

    user_data = cur.fetchall()
    conn.close()

    return render_template('show.html', user_data=user_data)


















UPLOAD_FOLDER = 'uploads'  # متغير فيه اسم أو مسار المجلد اللي هتخزن فيه الملفات
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf','mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # بتربط الإعداد الرسمي في Flask بالمجلد ده

#? 2. التحقق من امتداد الملف:
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#? 3. استلام الملف من الفورم:
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if 'user' not in session:
        flash("يجب تسجيل الدخول أولًا.")
        return redirect(url_for('login'))

    if request.method == "POST":
        file = request.files.get("file")

        if file and allowed_file(file.filename):
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + secure_filename(file.filename)
           
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(saved_path)

            # حفظ البيانات في قاعدة البيانات
            email = session['user']
            uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect('guestbooks.db')
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO uploads (email, filename, filepath, uploaded_at)
                VALUES (?, ?, ?, ?)
            ''', (email, filename, saved_path, uploaded_at))
            conn.commit()
            conn.close()

            flash("تم رفع الملف بنجاح!")
            return redirect(url_for('dashboard'))

        else:
            flash("امتداد الملف غير مسموح.")
    
    return render_template("upload.html")


@app.route("/show_upload_file",)
def show_upload_file():
    if 'user' not in session:
        flash("يجب تسجيل الدخول أولًا.")
        return redirect(url_for('login'))

    email = session['user']
    conn = sqlite3.connect('guestbooks.db')
    cur = conn.cursor()

    # استعلام يضم بيانات المستخدم مع السعرات الحرارية
    
    cur.execute("SELECT filename, filepath, uploaded_at FROM uploads WHERE email = ?", (email,))

    uploads = cur.fetchall()
    conn.close()

    return render_template("my_uploads.html", uploads=uploads)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#app.config['UPLOAD_FOLDER']:ده المجلد اللي فيه الملفات المرفوعة (مثلاً: 'uploads').
#send_from_directory(...):دي دالة جاهزة من Flask وظيفتها ترجع الملف للمستخدم عشان يحمله أو يشوفه في المتصفح.
#def uploaded_file(filename):هنا filename هي اسم الملف اللي اتحط في الرابط، وهو نفس اسم الملف اللي اتخزن وقت الرفع.
#@app.route('/uploads/<filename>'):أي رابط يبدأ بـ /uploads/اسم_ملف هيوصل للدالة دي، و<filename> معناها جزء متغير من الرابط (اسم الملف اللي المستخدم عايز يشوفه أو يحمله).

@app.route('/delete_file', methods=['POST'])
def delete_file():
    if 'user' not in session:
        flash("يجب تسجيل الدخول أولًا.")
        return redirect(url_for('login'))

    filename = request.form.get('filename')  # استلام اسم الملف
    email = session['user']  # الإيميل الخاص بالمستخدم الحالي

    if filename:
        # حذف من قاعدة البيانات
        conn = sqlite3.connect('guestbooks.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM uploads WHERE email = ? AND filename = ?", (email, filename))
        conn.commit()
        conn.close()

        # حذف من مجلد الملفات
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        flash("تم حذف الملف بنجاح.")
    else:
        flash("حدث خطأ أثناء حذف الملف.")

    return redirect(url_for('show_upload_file'))







if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)


