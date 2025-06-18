from flask import Flask
from flask import Flask, render_template
from quiz.routes import quiz_bp  # ✅ this should now work
from auth import auth_bp  # if you have login/register

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # make sure this is secure in production

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp, url_prefix='/quiz')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
