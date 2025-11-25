from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for,current_app
from flask_login import login_required, current_user
from app.models import Subject, Task, Schedule, Performance
from app import db
from datetime import datetime, timedelta
from flask_mail import Mail,Message

mail = Mail()
main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.deadline).limit(5).all()
    performances = Performance.query.filter_by(user_id=current_user.id).all()
    
    return render_template('main/dashboard.html', 
                         subjects=subjects,
                         tasks=tasks,
                         performances=performances)

@main.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        difficulty = request.form.get('difficulty')
        estimated_time = request.form.get('estimated_time')
        
        subject = Subject(
            name=name,
            difficulty_level=difficulty,
            estimated_time=estimated_time,
            user_id=current_user.id
        )
        db.session.add(subject)
        db.session.commit()
        
        flash('Subject added successfully!', 'success')
        return redirect(url_for('main.subjects'))
    
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('main/subjects.html', subjects=subjects)
@main.route('/subjects/<int:sub_id>/delete', methods=['POST'])
@login_required
def delete_sub(sub_id):
    subject = Subject.query.get_or_404(sub_id)
    if subject.user_id != current_user.id:
        flash('You are not authorized to delete this subject.', 'danger')
        return redirect(url_for('main.subjects'))
    
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('main.subjects'))
@main.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')  # Get title from form as description
        deadline_str = request.form.get('deadline')
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            # If time is not included, append default time (end of day)
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                deadline = deadline.replace(hour=23, minute=59)
            except ValueError:
                flash('Invalid deadline format. Please use the date picker.', 'danger')
                return redirect(url_for('main.subjects'))
                
        subject_id = request.form.get('subject_id')
        priority = request.form.get('priority')
        
        task = Task(
            title = title,
            description=description,
            deadline=deadline,
            subject_id=subject_id,
            priority=priority,
            status='Pending',
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        
        flash('Task added successfully!', 'success')
        return redirect(url_for('main.tasks'))
    
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.deadline).all()
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('main/tasks.html', tasks=tasks, subjects=subjects)

@main.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    print("STATUS RECEIVED FROM EDIT FORM:", task.status)
    if task.user_id != current_user.id:
        flash('You are not authorized to edit this task.', 'danger')
        return redirect(url_for('main.tasks'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        deadline_str = request.form.get('deadline')
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid deadline format', 'danger')
            return redirect(url_for('main.tasks'))
        
        subject_id = request.form.get('subject_id')
        priority = request.form.get('priority')
        status = request.form.get('status')
        
        # Store old subject_id to update performance if it changes
        old_subject_id = task.subject_id
        # Update task
        task.title = title
        task.description = description
        task.deadline = deadline
        task.subject_id = subject_id
        task.priority = priority
        task.status = status
        
        db.session.commit()
       
        
        
        # Update performance for both old and new subject if changed
        update_performance_metrics(current_user.id, old_subject_id)
        if old_subject_id != subject_id:
            update_performance_metrics(current_user.id, subject_id)
        
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.tasks'))
    
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('main/edit_task.html', task=task, subjects=subjects)

@main.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You are not authorized to delete this task.', 'danger')
        return redirect(url_for('main.tasks'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.tasks'))

@main.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        if not task_id:
            flash('Please select a task.', 'danger')
            return redirect(url_for('main.schedule'))
            
        task = Task.query.get_or_404(task_id)
        if task.user_id != current_user.id:
            flash('You are not authorized to schedule this task.', 'danger')
            return redirect(url_for('main.schedule'))
            
        try:
            date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
            end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
            
            # Validate times
            if start_time >= end_time:
                flash('End time must be after start time.', 'danger')
                return redirect(url_for('main.schedule'))
                
            # Check for schedule conflicts
            existing_schedules = Schedule.query.filter_by(
                user_id=current_user.id,
                date=date
            ).all()
            
            for existing in existing_schedules:
                if (start_time < existing.end_time and end_time > existing.start_time):
                    flash('This time slot conflicts with an existing schedule.', 'danger')
                    return redirect(url_for('main.schedule'))
            
            schedule = Schedule(
                date=date,
                start_time=start_time,
                end_time=end_time,
                task_id=task_id,
                user_id=current_user.id
            )
            db.session.add(schedule)
            db.session.commit()
            
            flash('Schedule created successfully!', 'success')
            return redirect(url_for('main.schedule'))
            
        except ValueError as e:
            flash('Invalid date or time format. Please use the date and time pickers.', 'danger')
            return redirect(url_for('main.schedule'))
    
    # Get all schedules ordered by date and time
    schedules = Schedule.query.filter_by(user_id=current_user.id)\
        .order_by(Schedule.date, Schedule.start_time).all()
    
    # Get incomplete tasks (pending or in progress)
    tasks = Task.query.filter_by(user_id=current_user.id)\
        .filter(Task.status.in_(['Pending', 'In Progress']))\
        .order_by(Task.deadline).all()
    
    if not tasks:
        flash('No tasks available for scheduling. Please create some tasks first.', 'info')
    
    return render_template('main/schedule.html', 
                         schedules=schedules, 
                         tasks=tasks,
                         now=datetime.now())

@main.route('/schedule/<int:schedule_id>/delete', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.user_id != current_user.id:
        flash('You are not authorized to delete this schedule.', 'danger')
        return redirect(url_for('main.schedule'))
    
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted successfully!', 'success')
    return redirect(url_for('main.schedule'))

def update_performance_metrics(user_id, subject_id):
    """Update performance metrics for a given subject"""
    # Get total and completed tasks for the subject
    total_tasks = Task.query.filter_by(user_id=user_id, subject_id=subject_id).count()
    completed_tasks = Task.query.filter_by(
        user_id=user_id,
        subject_id=subject_id,
        status='Completed'
    ).count()
    
    # Calculate progress percentage
    progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Update or create performance record
    performance = Performance.query.filter_by(
        user_id=user_id,
        subject_id=subject_id
    ).first()
    
    if performance:
        performance.progress = progress
        performance.last_updated = datetime.now()
    else:
        performance = Performance(
            user_id=user_id,
            subject_id=subject_id,
            progress=progress,
            last_updated=datetime.now()
        )
        db.session.add(performance)
    
    db.session.commit()

@main.route('/update_task_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    print("route reached")
    if task.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    new_status = request.form.get('status')
    if new_status not in ['Pending', 'In Progress', 'Completed']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    
    task.status = new_status
    db.session.commit()
    if new_status == "Completed":
        msg = Message(
            subject="Task Completed!",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=["deivikrajesh@gmail.com"],   # <-- put parent's email here
            body=f"{current_user.name} has just completed the task: {task.description}"
        )
        print("Sending email")
        mail.send(msg)
        print("Enail Sent ")
    
    # Update performance metrics
    update_performance_metrics(current_user.id, task.subject_id)
    
    return jsonify({'success': True})

@main.route('/performance')
@login_required
def performance():
    # Get all subjects for the user
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    
    # Update performance metrics for all subjects
    for subject in subjects:
        update_performance_metrics(current_user.id, subject.id)
    
    # Get updated performance records
    performances = Performance.query.filter_by(user_id=current_user.id).all()
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    return render_template('main/performance.html', performances=performances, tasks=tasks)
@main.route('/profile')
@login_required
def profile():
    # Get user details
    user = current_user

    # Count subjects
    total_subjects = Subject.query.filter_by(user_id=user.id).count()

    # Count tasks
    total_tasks = Task.query.filter_by(user_id=user.id).count()

    # Count completed tasks
    completed_tasks = Task.query.filter_by(user_id=user.id, status='Completed').count()

    # Calculate percentage
    if total_tasks > 0:
        percentage = round((completed_tasks / total_tasks) * 100, 2)
    else:
        percentage = 0

    # Motivational message
    if percentage >= 80:
        message = "🔥 Excellent! Keep it up!"
    elif percentage >= 40:
        message = "⚡ Keep Going! You're improving."
    else:
        message = "🚀 Hurry Up! You can do better!"

    return render_template('main/profile.html',
                           user=user,
                           total_subjects=total_subjects,
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           percentage=percentage,
                           message=message)