from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    subjects = db.relationship('Subject', backref='user', lazy=True, cascade = "all, delete")
    tasks = db.relationship('Task', backref='user', lazy=True, cascade = "all, delete")
    schedules = db.relationship('Schedule', backref='user', lazy=True, cascade = "all, delete")
    performances = db.relationship('Performance', backref='user', lazy=True, cascade = "all, delete")

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)  # Easy, Medium, Hard
    estimated_time = db.Column(db.Integer, nullable=False)  # in minutes
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete = 'CASCADE'), nullable=False)
    tasks = db.relationship('Task', backref='subject', lazy=True, cascade = "all, delete")
    performances = db.relationship('Performance', backref='subject', lazy=True, cascade = "all, delete")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200),nullable =False)
    description = db.Column(db.String(200) )
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    priority = db.Column(db.String(20), nullable=False)  # low, medium, high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete = 'CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id',ondelete = 'CASCADE'), nullable=False)
    schedules = db.relationship('Schedule', backref='task', lazy=True, cascade = "all, delete")

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete = 'CASCADE'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id',ondelete = 'CASCADE'), nullable=False)

class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    progress = db.Column(db.Float, default=0.0)  # percentage
    completion_time = db.Column(db.Integer, default=0)  # in minutes
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete = 'CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id',ondelete = 'CASCADE'), nullable=False)
