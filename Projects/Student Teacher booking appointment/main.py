import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import requests
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "<Setup your secret key (leave it for default usage)>"

# Initialize Firebase Admin SDK
cred = credentials.Certificate('path/to/your/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Firebase project configuration
firebase_api_key = '< Firebase API key here >'  # Replace with your Firebase API key

firebase_config = {
    'apiKey': '< Firebase API key here >',
    'projectId': '< Firebase project ID here >',
    'authDomain': '< Firebase auth Domain here >',
    'messagingSenderId': '< Firebase messaging sender id here >',
    'storageBucket': '< Firebase storage bucket here >',
    'appId': '< Firebase app ID here >'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            print("Unauthorized access attempt")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    print(f"Login attempt for user: {email}")
    
    # Call Firebase Authentication API to sign in the user
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = requests.post(auth_url, json=payload)
    data = response.json()
    
    if 'idToken' in data:
        id_token = data['idToken']
        
        try:
            # Verify the ID token using Firebase Admin SDK
            decoded_token = auth.verify_id_token(id_token)
            user_email = decoded_token['email']
            
            # Check user status in Firestore
            user_role = get_user_role(user_email)
            if user_role is None:
                flash('User role not found.')
                print("User role not found.")
                return redirect(url_for('home'))
            
            user_doc_ref = db.collection('users').document(user_email)
            user_doc = user_doc_ref.get()
            user_data = user_doc.to_dict()
            user_status = user_data.get('status', 'pending')
            
            if user_status == 'pending':
                flash('Your registration is pending approval. Please wait until an admin approves your registration.')
                print("Registration pending approval.")
                return redirect(url_for('home'))
            
            if user_status == 'approved':
                session['user'] = user_email  # Store the email in the session
                print(f"User {user_email} logged in with role {user_role}")
                
                if user_role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user_role == 'teacher':
                    return redirect(url_for('teacher_dashboard', email=user_email))
                elif user_role == 'student':
                    return redirect(url_for('student_dashboard', email=user_email))
                else:
                    flash('Unknown role.')
                    print("Unknown role.")
                    return redirect(url_for('home'))
            else:
                flash('Invalid user status.')
                print("Invalid user status.")
                return redirect(url_for('home'))
                
        except Exception as e:
            flash(f'Error: {str(e)}')
            print(f"Error during login: {e}")
            return redirect(url_for('home'))
    else:
        flash('Invalid credentials.')
        print("Invalid credentials.")
        return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    role = "student"
    
    print(f"Register attempt for user: {email} with role {role}")
    
    try:
        # Create user in Firebase Auth
        auth.create_user(email=email, password=password)
        # Save user role as student in Firestore
        db.collection('users').document(email).set({'role': role, 'status': 'pending'})
        flash('Registration successful. Your account is pending approval.')
        print("Registration successful, pending approval.")
        return redirect('/')
    except Exception as e:
        flash(f'Error: {str(e)}')
        print(f"Error during registration: {e}")
        return redirect('/register')

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    email = request.args.get('email')
    student_id = email  # Assuming email as student ID
    
    print(f"Loading student dashboard for: {student_id}")
    
    appointments = get_student_appointments(student_id)
    teachers = get_all_teachers()  # Fetch the list of teachers
    
    print(f"Appointments: {appointments}")
    print(f"Teachers: {teachers}")
    
    return render_template('student_dashboard.html', appointments=appointments, teachers=teachers, student_id=student_id)

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    email = request.args.get('email')
    teacher_id = email  # Assuming email as teacher ID
    
    print(f"Loading teacher dashboard for: {teacher_id}")
    
    appointments, messages = get_teacher_dashboard(teacher_id)
    print(f"Appointments: {appointments}")
    print(f"Messages: {messages}")
    
    return render_template('teacher_dashboard.html', appointments=appointments, messages=messages, firebase_config=firebase_config)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if get_user_role(session['user']) != 'admin':
        print("Unauthorized admin dashboard access attempt")
        return redirect(url_for('home'))

    print("Loading admin dashboard")
    
    # Fetch all students with pending status
    pending_students = get_pending_students()
    print(f"Pending students: {pending_students}")

    # Fetch all teachers
    teachers = get_all_teachers()
    print(f"Teachers: {teachers}")

    return render_template('admin_dashboard.html', pending_students=pending_students, teachers=teachers)

@app.route('/admin_add_teacher', methods=['GET', 'POST'])
@login_required
def admin_add_teacher():
    if get_user_role(session['user']) != 'admin':
        print("Unauthorized admin add teacher access attempt")
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        subject = request.form['subject']
        
        print(f"Adding teacher: {name}, Department: {department}, Subject: {subject}")
        
        try:
            # Add teacher to Firestore
            db.collection('teachers').add({
                'name': name,
                'department': department,
                'subject': subject
            })
            print(f"Teacher {name} added successfully")
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            print(f"Error adding teacher: {e}")
            return str(e), 400

    return render_template('admin_add_teacher.html')

@app.route('/admin_delete_teacher/<teacher_id>', methods=['POST'])
@login_required
def admin_delete_teacher(teacher_id):
    if get_user_role(session['user']) != 'admin':
        print("Unauthorized admin delete teacher access attempt")
        return redirect(url_for('home'))

    print(f"Deleting teacher with ID: {teacher_id}")
    
    try:
        # Delete teacher from Firestore
        db.collection('teachers').document(teacher_id).delete()
        print(f"Teacher {teacher_id} deleted successfully")
        return redirect(url_for('admin_manage_teachers'))
    except Exception as e:
        print(f"Error deleting teacher: {e}")
        return str(e), 500

@app.route('/admin_manage_teachers')
@login_required
def admin_manage_teachers():
    if get_user_role(session['user']) != 'admin':
        print("Unauthorized admin manage teachers access attempt")
        return redirect(url_for('home'))

    print("Loading admin manage teachers page")
    
    teachers = get_all_teachers()
    print(f"Teachers: {teachers}")
    
    return render_template('admin_manage_teachers.html', teachers=teachers)

@app.route('/admin_approve_student/<student_id>', methods=['POST'])
@login_required
def admin_approve_student(student_id):
    if get_user_role(session['user']) != 'admin':
        print("Unauthorized admin approve student access attempt")
        return redirect(url_for('home'))

    print(f"Approving student with ID: {student_id}")
    
    try:
        # Approve student by updating status in Firestore
        db.collection('users').document(student_id).update({'status': 'approved'})
        print(f"Student {student_id} approved")
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"Error approving student: {e}")
        return str(e), 400

@app.route('/admin_delete_student/<student_id>', methods=['DELETE'])
@login_required
def admin_delete_student(student_id):
    if get_user_role(session['user']) != 'admin':
        print("Unauthorized admin delete student access attempt")
        return redirect(url_for('home'))

    print(f"Deleting student with ID: {student_id}")
    
    try:
        # Delete student from Firestore
        db.collection('users').document(student_id).delete()
        print(f"Student {student_id} deleted successfully")
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error deleting student: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    student_id = request.form['studentId']
    teacher_id = request.form['teacherId']
    date = request.form['date']
    time = request.form['time']
    
    print(f"Booking appointment for student {student_id} with teacher {teacher_id} on {date} at {time}")
    
    try:
        db.collection('appointments').add({
            'studentId': student_id,
            'teacherId': teacher_id,
            'date': date,
            'time': time,
            'status': 'pending'
        })
        print("Appointment booked successfully")
        return redirect(url_for('student_dashboard', email=student_id))
    except Exception as e:
        print(f"Error booking appointment: {e}")
        return str(e), 400

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    student_id = request.form['studentId']
    teacher_id = request.form['teacherId']
    content = request.form['content']
    
    print(f"Sending message from student {student_id} to teacher {teacher_id}: {content}")
    
    try:
        db.collection('messages').add({
            'studentId': student_id,
            'teacherId': teacher_id,
            'content': content
        })
        print("Message sent successfully")
        return redirect(url_for('student_dashboard', email=student_id))
    except Exception as e:
        print(f"Error sending message: {e}")
        return str(e), 400

def get_user_role(email):
    print(f"Fetching role for user: {email}")
    try:
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()
        role = doc.to_dict().get('role')
        print(f"Role for user {email}: {role}")
        return role
    except Exception as e:
        print(f"Error fetching role: {e}")
        return None

def get_student_appointments(student_id):
    print(f"Fetching appointments for student: {student_id}")
    try:
        appointments = db.collection('appointments').where('studentId', '==', student_id).stream()
        result = [{'teacherId': doc.to_dict().get('teacherId'),
                   'date': doc.to_dict().get('date'),
                   'time': doc.to_dict().get('time'),
                   'status': doc.to_dict().get('status')} for doc in appointments]
        print(f"Appointments for student {student_id}: {result}")
        return result
    except Exception as e:
        print(f"Error fetching appointments: {e}")
        return []

def get_teacher_dashboard(teacher_id):
    print(f"Fetching dashboard data for teacher: {teacher_id}")
    try:
        appointments = db.collection('appointments').where('teacherId', '==', teacher_id).stream()
        messages = db.collection('messages').where('teacherId', '==', teacher_id).stream()
        appointments_list = [{'studentId': doc.to_dict().get('studentId'),
                              'date': doc.to_dict().get('date'),
                              'time': doc.to_dict().get('time'),
                              'status': doc.to_dict().get('status')} for doc in appointments]
        messages_list = [{'studentId': doc.to_dict().get('studentId'),
                          'content': doc.to_dict().get('content')} for doc in messages]
        print(f"Dashboard data for teacher {teacher_id}: Appointments: {appointments_list}, Messages: {messages_list}")
        return appointments_list, messages_list
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return [], []

def get_pending_students():
    print("Fetching pending students")
    try:
        students_ref = db.collection('users').where('role', '==', 'student').where('status', '==', 'pending')
        students = students_ref.stream()
        result = [{'email': doc.id, 'status': doc.to_dict().get('status', 'pending')} for doc in students]
        print(f"Pending students: {result}")
        return result
    except Exception as e:
        print(f"Error fetching pending students: {e}")
        return []

def get_all_teachers():
    print("Fetching all teachers")
    try:
        teachers_ref = db.collection('users').where('role', '==', 'teacher')
        teachers = teachers_ref.stream()
        result = [{'id': doc.id,
                   'name': doc.to_dict().get('name', 'Unknown'),
                   'department': doc.to_dict().get('department', 'Unknown'),
                   'subject': doc.to_dict().get('subject', 'Unknown')} for doc in teachers]
        print(f"Teachers: {result}")
        return result
    except Exception as e:
        print(f"Error fetching teachers: {e}")
        return []

@app.route('/logout')
def logout():
    session.clear()
    print("User logged out")
    return "<script> window.location = window.location.origin </script> "

if __name__ == '__main__':
    app.run(host="0.0.0.0")
