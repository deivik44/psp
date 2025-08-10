# Study Planner Application

A Flask-based web application for managing your study tasks, schedules, and tracking performance.

## Features

- **Task Management**
  - Create, edit, and delete tasks
  - Set task priorities and deadlines
  - Track task status (Pending, In Progress, Completed)

- **Schedule Management**
  - Create study schedules for tasks
  - Avoid time slot conflicts
  - View all scheduled study sessions

- **Performance Tracking**
  - Track progress by subject
  - View completion rates
  - Visual progress bars

- **User Authentication**
  - Secure user registration and login
  - Password hashing for security
  - User-specific data isolation

## Setup Instructions

1. **Prerequisites**
   - Python 3.8 or higher
   - pip (Python package installer)

2. **Extract the Project**
   - Extract the study_planner.zip file to your desired location

3. **Create Virtual Environment** (Optional but recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the Database**
   ```bash
   # Windows
   python
   >>> from app import db, create_app
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()

   # Linux/Mac
   python3
   >>> from app import db, create_app
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

6. **Run the Application**
   ```bash
   # Windows
   python run.py

   # Linux/Mac
   python3 run.py
   ```

7. **Access the Application**
   - Open your web browser
   - Go to: http://localhost:5000
   - Register a new account to get started

## Usage Guide

1. **Getting Started**
   - Register a new account
   - Log in to your account
   - Create subjects for your studies

2. **Managing Tasks**
   - Click "Tasks" in the navigation menu
   - Use the form to create new tasks
   - Set description, subject, deadline, and priority
   - Edit or delete tasks using the buttons

3. **Creating Schedules**
   - Go to "Schedule" in the navigation menu
   - Select a task from the dropdown
   - Choose date and time slot
   - View your schedule in the table

4. **Tracking Performance**
   - Visit "Performance" in the navigation menu
   - View progress for each subject
   - See completion rates and statistics

## File Structure
```
study_planner/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   └── templates/
│       ├── base.html
│       ├── auth/
│       └── main/
├── instance/
│   └── study_planner.db
├── venv/
├── requirements.txt
├── run.py
└── README.md
```

## Troubleshooting

1. **Database Issues**
   - If you get database errors, ensure you've initialized the database
   - Delete the `instance/study_planner.db` file and reinitialize if needed

2. **Dependencies**
   - If you get import errors, ensure all dependencies are installed:
     ```bash
     pip install -r requirements.txt
     ```

3. **Port in Use**
   - If port 5000 is in use, modify `run.py` to use a different port:
     ```python
     app.run(port=5001)
     ```

## Security Notes

- Never share your database file
- Keep your virtual environment in `.gitignore`
- Change the secret key in production
- Use HTTPS in production environment

## Support

For issues or questions:
1. Check the troubleshooting section
2. Ensure all setup steps were followed
3. Verify Python and dependency versions
4. Check for error messages in the console

