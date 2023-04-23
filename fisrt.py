from flask import Flask, request, render_template
import sqlite3
import smtplib

app = Flask(__name__)

conn = sqlite3.connect('forum.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS questions
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              content TEXT NOT NULL,
              category TEXT NOT NULL,
              user_id INTEGER NOT NULL,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);''')


c.execute('''CREATE TABLE IF NOT EXISTS answers
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              content TEXT NOT NULL,
              question_id INTEGER NOT NULL,
              user_id INTEGER NOT NULL,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);''')

c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT NOT NULL,
              password TEXT NOT NULL);''')


def send_notification(user_email, message):
    sender_email = "vamsikrishna2330@gmail.com"
    password = "Vamsi#4032"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, user_email, message)
    server.quit()
@app.route('/')
def index():
    c.execute('''SELECT DISTINCT category FROM questions;''')
    categories = c.fetchall()
    c.execute('''SELECT q.id, q.title, q.timestamp, u.email
                 FROM questions q
                 JOIN users u ON q.user_id = u.id
                 ORDER BY q.timestamp DESC
                 LIMIT 10;''')
    questions = c.fetchall()
    return render_template('index.html', categories=categories, questions=questions)
@app.route('/question/new', methods=['GET', 'POST'])
def new_question():
    if request.method == 'POST':
        # Insert new question into the database
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        user_id = 1  # TODO: Get user ID from session
        c.execute('''INSERT INTO questions (title, content, category, user_id)
                     VALUES (?, ?, ?, ?);''', (title, content, category, user_id))
        conn.commit()

        # Send email notification to user
        user_email = "user@example.com"  # TODO: Get user email from session
        message = "Your question has been posted."
        send_notification(user_email, message)

        return redirect('/')
    else:
        # Show form for creating a new question
        return render_template('new_question.html')

# Page for viewing a question and its answers
@app.route('/question/<int:id>', methods=['GET', 'POST'])
def view_question(id):
    if request.method == 'POST':
        # Insert new answer into the database
        content = request.form['content']
        user_id = 1  # TODO: Get user ID from session
        c.execute('''INSERT INTO answers (content, question_id, user_id)
                     VALUES (?, ?, ?);''', (content, id, user_id))
        conn.commit()

        # Send email notification to user who posted the question
        c.execute('''SELECT u.email, q.title
                     FROM questions q
                     JOIN users u ON q.user_id = u.id
                     WHERE q.id''')
if __name__ == '__main__':
    app.run()