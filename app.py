from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    program = db.Column(db.String(100), nullable=False)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()
    if not News.query.first():
        db.session.add(News(date="2026-10-12", title="Шинэ хичээлийн жилийн элсэлт эхэллээ"))
        db.session.add(News(date="2026-10-01", title="Оюутнуудын дунд спортын тэмцээн болно"))
        db.session.commit()

programs = {
    "web-programming": {
        "name": "Вэб програмчлал",
        "icon": "💻",
        "description": "Вэб сайт болон веб систем боловсруулах чиглэлээр мэргэжлийн мэдлэг, ур чадвар эзэмшинэ."
    },
    "graphic-design": {
        "name": "Хэвлэлийн график дизайн",
        "icon": "🎨",
        "description": "Хэвлэлийн болон график дизайны бүтээгдэхүүн боловсруулах ур чадвар эзэмшинэ."
    },
    "hairdressing": {
        "name": "Үсчин",
        "icon": "💇",
        "description": "Үс засалт, хэлбэржүүлэлт, будаг болон гоо сайхны үйлчилгээний ур чадвар эзэмшинэ."
    },
    "tourism": {
        "name": "Аялал жуулчлал",
        "icon": "✈️",
        "description": "Аялал жуулчлалын үйлчилгээ, аяллын хөтөлбөр боловсруулах мэдлэг эзэмшинэ."
    },
    "office": {
        "name": "Оффис бичиг хэрэг",
        "icon": "📑",
        "description": "Албан хэрэг хөтлөлт, бичиг баримт боловсруулах ур чадвар эзэмшинэ."
    },
    "beauty": {
        "name": "Гоо засалч",
        "icon": "💄",
        "description": "Гоо сайхны үйлчилгээ, нүүр будалт, арьс арчилгааны ур чадвар эзэмшинэ."
    },
    "nursing": {
        "name": "Сувилагч",
        "icon": "🩺",
        "description": "Эрүүл мэндийн байгууллагад сувилахуйн тусламж үйлчилгээ үзүүлэх ур чадвар эзэмшинэ."
    },
    "accounting": {
        "name": "Нярав",
        "icon": "💰",
        "description": "Байгууллагын бараа материал, хөрөнгийн бүртгэл хөтлөх мэдлэг эзэмшинэ."
    },
    "stage-screen": {
        "name": "Тайз дэлгэц",
        "icon": "🎬",
        "description": "Тайз, дэлгэцийн бүтээл, зураг авалт, техникийн чиглэлээр мэдлэг эзэмшинэ."
    },
    "fashion-design": {
        "name": "Хувцас дизайн",
        "icon": "👗",
        "description": "Хувцас загвар зохион бүтээх, эсгүүр хийх, оёх ур чадвар эзэмшинэ."
    },
    "construction": {
        "name": "Барилга",
        "icon": "🏗️",
        "description": "Барилгын технологи, зураг төсөл, барилгын ажил гүйцэтгэх мэдлэг эзэмшинэ."
    }
}

@app.route("/")
def index():
    news_items = News.query.order_by(News.id.desc()).all()
    return render_template("index.html", programs=programs, news=news_items)

@app.route("/hutulbur")
def hutulbur():
    return render_template("hutulbur.html", programs=programs)

@app.route("/hutulbur/<program_slug>")
def program_detail(program_slug):
    program = programs.get(program_slug)
    if program is None:
        return "Хөтөлбөр олдсонгүй", 404
    return render_template("program_detail.html", program=program)

@app.route("/register", methods=["POST"])
def register():
    new_reg = Registration(
        fullname=request.form.get("fullname"),
        phone=request.form.get("phone"),
        email=request.form.get("email"),
        program=request.form.get("program")
    )
    db.session.add(new_reg)
    db.session.commit()
    return redirect(url_for('index') + '#register')

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session['logged_in'] = True
            return redirect(url_for('view_submissions'))
        else:
            error = "Нэвтрэх нэр эсвэл нууц үг буруу байна!"
    return render_template("login.html", error=error)

@app.route("/admin/submissions")
def view_submissions():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template("admin.html", 
                         registrations=Registration.query.order_by(Registration.id.desc()).all(), 
                         news=News.query.order_by(News.id.desc()).all())

@app.route("/admin/news/add", methods=["POST"])
def add_news():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    date = request.form.get("date")
    title = request.form.get("title")
    if date and title:
        db.session.add(News(date=date, title=title))
        db.session.commit()
    return redirect(url_for('view_submissions'))

@app.route("/admin/news/delete/<int:news_id>")
def delete_news(news_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    db.session.delete(News.query.get_or_404(news_id))
    db.session.commit()
    return redirect(url_for('view_submissions'))

@app.route("/admin/registration/delete/<int:reg_id>")
def delete_registration(reg_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    db.session.delete(Registration.query.get_or_404(reg_id))
    db.session.commit()
    return redirect(url_for('view_submissions'))

@app.route("/admin/logout")
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == "__main__":
    app.run(debug=True)