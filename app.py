from flask import Flask, render_template, request, redirect, session, url_for, Blueprint
from config import Config
from db import SessionLocal, User, DailyInput, MonthlyTheme, WeeklyQuestion
from datetime import datetime, timedelta
import pytz
import os

app = Flask(__name__)
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.config.from_object(Config)
app.config["PROPAGATE_EXCEPTIONS"] = True

bp = Blueprint("daily", __name__)

# -----------------------------
# / → /login
# -----------------------------
@app.route("/")
def index():
    return redirect(url_for("login"))

# -----------------------------
# ログイン
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    with SessionLocal() as db:
        if request.method == "POST":
            user_id = request.form.get("user_id")
            password = request.form.get("password")
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user or password != user.password_hash:
                error = "ユーザーIDまたはパスワードが違います"
            else:
                session["user_id"] = user.id
                session["user_name"] = user.name_kanji
                session["current_date"] = datetime.now(
                    pytz.timezone("Asia/Tokyo")
                ).strftime("%Y-%m-%d")
                return redirect(url_for("daily_input"))

        # 今月のテーマ
        today = datetime.now(pytz.timezone("Asia/Tokyo"))
        monthly = db.query(MonthlyTheme).filter(
            MonthlyTheme.year == today.year,
            MonthlyTheme.month == today.month
        ).first()
        monthly_theme = monthly.theme_text if monthly else "（今月のテーマ未登録）"

    return render_template("login.html", error=error, monthly_theme=monthly_theme)

# -----------------------------
# 今日の入力（メイン）
# -----------------------------
@app.route("/daily_input", methods=["GET", "POST"])
@app.route("/daily_input/<int:view_user_id>", methods=["GET", "POST"])
def daily_input(view_user_id=None):
    if "user_id" not in session:
        return redirect(url_for("login"))

    with SessionLocal() as db:
        current_user = db.query(User).filter(User.id == session["user_id"]).first()

        # 日付取得
        date_str = request.args.get("date")
        if date_str:
            try:
                today = datetime.strptime(date_str, "%Y-%m-%d").date()
                session["current_date"] = date_str
            except:
                today = datetime.strptime(session.get("current_date"), "%Y-%m-%d").date()
        else:
            today = datetime.strptime(session.get("current_date"), "%Y-%m-%d").date()

        # 管理者の他人参照モード
        if view_user_id and current_user.role == "admin" and view_user_id != current_user.id:
            viewing_user = db.query(User).filter(User.id == view_user_id).first()
            target_user = viewing_user
            viewing = True
        else:
            viewing_user = None
            target_user = current_user
            viewing = False

        # POST（保存）
        if request.method == "POST" and not viewing:
            try:
                existing = db.query(DailyInput).filter(
                    DailyInput.user_id == target_user.id,
                    DailyInput.date == today
                ).first()

                if existing:
                    existing.answer = request.form.get("answer")
                    existing.today_goal = request.form.get("today_goal")
                    existing.virtue = request.form.get("virtue")
                    existing.virtue2 = request.form.get("virtue2")
                    existing.goal_score = request.form.get("goal_score")
                    existing.reflection = request.form.get("reflection")
                    existing.thanks = request.form.get("thanks")
                    existing.apply_learning = request.form.get("apply_learning")
                else:
                    new_row = DailyInput(
                        user_id=target_user.id,
                        date=today,
                        answer=request.form.get("answer"),
                        today_goal=request.form.get("today_goal"),
                        virtue=request.form.get("virtue"),
                        virtue2=request.form.get("virtue2"),
                        goal_score=request.form.get("goal_score"),
                        reflection=request.form.get("reflection"),
                        thanks=request.form.get("thanks"),
                        apply_learning=request.form.get("apply_learning"),
                    )
                    db.add(new_row)

                db.commit()
                return redirect(
                    url_for("daily_input", view_user_id=view_user_id, date=today.strftime("%Y-%m-%d"))
                    if viewing else
                    url_for("daily_input", date=today.strftime("%Y-%m-%d"))
                )
            except Exception as e:
                db.rollback()
                return f"保存エラー: {e}"

        # GET（表示）
        existing = db.query(DailyInput).filter(
            DailyInput.user_id == target_user.id,
            DailyInput.date == today
        ).first()

        form_data = {
            "answer": existing.answer if existing else "",
            "today_goal": existing.today_goal if existing else "",
            "virtue": existing.virtue if existing else "",
            "goal_score": existing.goal_score if existing and existing.goal_score is not None else "50",
            "reflection": existing.reflection if existing else "",
            "thanks": existing.thanks if existing else "",
            "apply_learning": existing.apply_learning if existing else "",
            "virtue2": existing.virtue2 if existing else "",
        }

        virtues = [
            "挨拶", "笑顔", "言葉", "親切", "約束", "責任",
            "前向き", "尊重", "努力", "誠実", "自律", "健康", "感謝"
        ]

        virtues2 = [
            "挨拶", "笑顔", "言葉", "親切", "約束", "責任",
            "前向き", "尊重", "努力", "誠実", "自律", "健康", "感謝"
        ]

        # 今月のテーマ
        monthly = db.query(MonthlyTheme).filter(
            MonthlyTheme.year == today.year,
            MonthlyTheme.month == today.month
        ).first()
        monthly_theme = monthly.theme_text if monthly else "（今月のテーマ未登録）"
        monthly_page_num = monthly.pages if monthly else 1

        # 今週の質問
        # 今日以前で最も直近の week_start_date を取得
        weekly = (
            db.query(WeeklyQuestion)
            .filter(WeeklyQuestion.week_start_date <= today)
            .order_by(WeeklyQuestion.week_start_date.desc())
            .first()
        )

        # レコードがある場合はその値を、ない場合はデフォルト値を代入
        if weekly:
            weekly_start_date = weekly.week_start_date
            weekly_question = weekly.question_text
            weekly_page_num = weekly.pages
        else:
            weekly_question = "（今週の質問未登録）"
            weekly_page_num = 1  # レコードがない場合は1ページ目をデフォルトに

        import os
        pdf_filename = f"theme_{today.year}_{today.month:02}.pdf"
        pdf_path = os.path.join(app.static_folder, 'pdf', pdf_filename)

        if os.path.exists(pdf_path):
            # PDF の最終更新日時を cache_buster にする
            cache_buster = int(os.path.getmtime(pdf_path))
        else:
            cache_buster = 0

        context = {
            "user_name": target_user.name_kanji,
            "display_date": today.strftime("%Y/%m/%d"),
            "monthly_theme": monthly_theme,
            "monthly_page_num": monthly_page_num,
            "weekly_start_date": weekly_start_date.strftime("%Y-%m-%d"),
            "weekly_question": weekly_question,
            "weekly_page_num": weekly_page_num,
            "virtues": virtues,
            "virtues2": virtues2,
            "form_data": form_data,
            "user": current_user,
            "users": db.query(User).order_by(User.name_kana).all() if current_user.role == "admin" else [],
            "viewing_user": viewing_user,
            "viewing": viewing,
            "view_user_id": view_user_id,
            "cache_buster": cache_buster,
        }

    return render_template("daily_input.html", **context)

# -----------------------------
# 発表用ページ
# -----------------------------
@app.route('/announcement')
def announcement():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # 表示対象のユーザーIDを取得（管理者用・自分用）
    v_user_id = request.args.get('view_user_id')
    target_user_id = int(v_user_id) if v_user_id and v_user_id != 'None' else session["user_id"]
    
    # 表示対象の日付を取得
    date_str = request.args.get('date') or session.get("current_date")

    with SessionLocal() as db:
        # ユーザー情報の取得
        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            return "ユーザーが見つかりません", 404
        
        user_name = target_user.name_kanji
        current_date_dt = datetime.strptime(date_str, '%Y-%m-%d')
        yesterday_dt = current_date_dt - timedelta(days=1)

        # 1. 今週の質問とPDFページ計算用データの取得
        weekly = db.query(WeeklyQuestion).filter(
            WeeklyQuestion.week_start_date <= current_date_dt.date()
        ).order_by(WeeklyQuestion.week_start_date.desc()).first()

        if weekly:
            weekly_question = weekly.question_text
            weekly_page_num = weekly.pages
            weekly_start_date = weekly.week_start_date.strftime("%Y-%m-%d")
        else:
            weekly_question = "（今週の質問未登録）"
            weekly_page_num = 1
            weekly_start_date = current_date_dt.strftime("%Y-%m-%d")

        # 2. 今月のテーマの取得
        monthly = db.query(MonthlyTheme).filter(
            MonthlyTheme.year == current_date_dt.year,
            MonthlyTheme.month == current_date_dt.month
        ).first()
        monthly_theme = monthly.theme_text if monthly else "（今月のテーマ未登録）"

        # 3. 当日のデータ（今日の準備・目標管理シート）の取得
        current_entry = db.query(DailyInput).filter(
            DailyInput.user_id == target_user.id,
            DailyInput.date == current_date_dt.date()
        ).first()

        form_data = {
            'answer': current_entry.answer if current_entry else "",
            'today_goal': current_entry.today_goal if current_entry else "",
            'virtue': current_entry.virtue if current_entry else "",
            'virtue2': current_entry.virtue2 if current_entry else "",
            'apply_learning': current_entry.apply_learning if current_entry else ""
        }

        # 4. 前日のデータ（昨日の振り返り）の取得
        yesterday_entry = db.query(DailyInput).filter(
            DailyInput.user_id == target_user.id,
            DailyInput.date == yesterday_dt.date()
        ).first()

        yesterday_data = {
            'reflection': yesterday_entry.reflection if yesterday_entry else "",
            'thanks': yesterday_entry.thanks if yesterday_entry else "",
            'goal_score': yesterday_entry.goal_score if yesterday_entry else 0
        }

        # 5. 日本語曜日の計算と日付フォーマット
        jp_weeks = ["月", "火", "水", "木", "金", "土", "日"]
        curr_w = jp_weeks[current_date_dt.weekday()]
        yest_w = jp_weeks[yesterday_dt.weekday()]
        
        formatted_current = f"{current_date_dt.strftime('%Y/%m/%d')}({curr_w})"
        formatted_yesterday = f"{yesterday_dt.strftime('%Y/%m/%d')}({yest_w})"

        # 6. PDFバナー用の情報
        pdf_filename = f"theme_{current_date_dt.year}_{current_date_dt.month:02}.pdf"
        pdf_path = os.path.join(app.static_folder, 'pdf', pdf_filename)
        cache_buster = int(os.path.getmtime(pdf_path)) if os.path.exists(pdf_path) else 0

    # テンプレートにすべての変数を渡す
    return render_template('announcement.html', 
                           user_name=user_name, 
                           form_data=form_data, 
                           yesterday_data=yesterday_data,
                           display_date=formatted_current,
                           yesterday_display_date=formatted_yesterday,
                           monthly_theme=monthly_theme,
                           weekly_question=weekly_question,
                           weekly_page_num=weekly_page_num,
                           weekly_start_date=weekly_start_date,
                           pdf_filename=pdf_filename,
                           cache_buster=cache_buster)

# -----------------------------
# 日付変更
# -----------------------------
@app.route("/set_date/<string:new_date>")
def set_date(new_date):
    session["current_date"] = new_date
    return redirect(url_for("daily_input"))

# -----------------------------
# 徳目リーダー
# -----------------------------
@app.route("/book")
def book_view():
    return render_template("book_view.html")

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
