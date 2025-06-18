from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from . import quiz_bp
from db import quizzes_col, scores_col

@quiz_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    quizzes = quizzes_col.find()
    return render_template('dashboard.html', quizzes=quizzes)

@quiz_bp.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # ✅ Only admin can access this route
    if session.get('role') != 'admin':
        flash("Only admins can create quizzes.")
        return redirect(url_for('quiz.dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        topic = request.form['topic']
        questions = []
        for i in range(1, 4):
            q = request.form[f'q{i}']
            options = [
                request.form[f'q{i}_opt1'],
                request.form[f'q{i}_opt2'],
                request.form[f'q{i}_opt3'],
                request.form[f'q{i}_opt4']
            ]
            answer = request.form[f'q{i}_ans']
            questions.append({
                "question": q,
                "options": options,
                "answer": answer
            })

        quizzes_col.insert_one({
            "title": title,
            "topic": topic,
            "questions": questions,
            "creator_id": session['user_id']
        })

        flash("Quiz created successfully!")
        return redirect(url_for('quiz.dashboard'))

    return render_template('create_quiz.html')

@quiz_bp.route('/take_quiz/<quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    quiz = quizzes_col.find_one({"_id": ObjectId(quiz_id)})
    if not quiz:
        flash("Quiz not found.")
        return redirect(url_for('quiz.dashboard'))

    if request.method == 'POST':
        score = 0
        total = len(quiz['questions'])

        for i, q in enumerate(quiz['questions']):
            selected_option = request.form.get(f'q{i}', '').strip().lower()
            correct_answer = q['answer'].strip().lower()

            if selected_option == correct_answer:
                score += 1

        scores_col.insert_one({
            "user_id": session['user_id'],
            "quiz_id": quiz_id,
            "score": score
        })

        return render_template('result.html', score=score, total=total)

    return render_template('take_quiz.html', quiz=quiz)

@quiz_bp.route('/scores')
def scores():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_scores = scores_col.find({"user_id": session['user_id']})
    return render_template('scores.html', scores=user_scores)

@quiz_bp.route('/quiz/edit/<quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    quiz = quizzes_col.find_one({'_id': ObjectId(quiz_id)})
    if not quiz:
        flash("Quiz not found.")
        return redirect(url_for('quiz.dashboard'))

    # ✅ Only admin can edit quizzes
    if session.get('role') != 'admin':
        flash("Only admins can edit quizzes.")
        return redirect(url_for('quiz.dashboard'))

    if request.method == 'POST':
        updated_title = request.form['title']
        updated_topic = request.form['topic']
        updated_questions = []

        for i in range(1, 4):
            q = request.form[f'q{i}']
            options = [
                request.form[f'q{i}_opt1'],
                request.form[f'q{i}_opt2'],
                request.form[f'q{i}_opt3'],
                request.form[f'q{i}_opt4']
            ]
            answer = request.form[f'q{i}_ans']
            updated_questions.append({
                "question": q,
                "options": options,
                "answer": answer
            })

        quizzes_col.update_one({'_id': ObjectId(quiz_id)}, {
            '$set': {
                'title': updated_title,
                'topic': updated_topic,
                'questions': updated_questions
            }
        })

        flash("Quiz updated successfully!")
        return redirect(url_for('quiz.dashboard'))

    return render_template('edit_quiz.html', quiz=quiz)

@quiz_bp.route('/quiz/delete/<quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    quiz = quizzes_col.find_one({'_id': ObjectId(quiz_id)})
    if not quiz:
        flash("Quiz not found.")
        return redirect(url_for('quiz.dashboard'))

    # ✅ Only admin can delete quizzes
    if session.get('role') != 'admin':
        flash("Only admins can delete quizzes.")
        return redirect(url_for('quiz.dashboard'))

    quizzes_col.delete_one({'_id': ObjectId(quiz_id)})
    flash("Quiz deleted successfully!")
    return redirect(url_for('quiz.dashboard'))

@quiz_bp.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Access denied.")
        return redirect(url_for('quiz.dashboard'))

    from db import users_col  # Avoid circular import

    # Create a user_id -> username map
    user_map = {}
    for user in users_col.find({}, {'_id': 1, 'username': 1}):
        user_map[str(user['_id'])] = user['username']

    # Get all quizzes and attach creator name
    all_quizzes = list(quizzes_col.find())
    for quiz in all_quizzes:
        quiz['creator_name'] = user_map.get(quiz.get('creator_id', ''), 'Unknown')

    # Get all scores and attach user name
    all_scores = list(scores_col.find())
    for score in all_scores:
        score['username'] = user_map.get(score.get('user_id', ''), 'Unknown')

    # Get all users (except password)
    all_users = list(users_col.find({}, {'password': 0}))

    return render_template(
        'admin_dashboard.html',
        users=all_users,
        scores=all_scores,
        quizzes=all_quizzes
    )
