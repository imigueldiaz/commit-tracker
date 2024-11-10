from app import db
from datetime import datetime

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    commits = db.relationship('Commit', backref='branch', lazy=True)

    def __repr__(self):
        return f'<Branch {self.name}>'

class Commit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commit_number = db.Column(db.String(50), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    commit_message = db.Column(db.String(200), nullable=False)
    long_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attachments = db.relationship('Attachment', backref='commit', lazy=True,
                                cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Commit {self.commit_number}>'

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    data = db.Column(db.LargeBinary)
    commit_id = db.Column(db.Integer, db.ForeignKey('commit.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attachment {self.filename}>'