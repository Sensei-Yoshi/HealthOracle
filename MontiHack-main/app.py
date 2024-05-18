from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import openai

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

openai.api_key = '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'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symptoms = db.Column(db.String(500), nullable=False)
    diagnosis = db.Column(db.String(500), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        symptoms = request.form['symptoms']
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Give advice on severity and if medical care is necessary"},
                {"role": "user", "content": f"I have the following symptoms: {symptoms}. What possible conditions could these symptoms indicate?"}
            ]
        )
        diagnosis = response.choices[0].message['content'].strip()
        post = Post(symptoms=symptoms, diagnosis=diagnosis)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_post.html')

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        comment_content = request.form['content']
        comment = Comment(content=comment_content, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post_id))
    comments = Comment.query.filter_by(post_id=post_id).all()
    return render_template('post_detail.html', post=post, comments=comments)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


