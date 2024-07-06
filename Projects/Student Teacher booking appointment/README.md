
# Student Teacher Appointment Booking WebApp

This application is a student-teacher booking appointment system designed to facilitate the scheduling of appointments and communication between students and teachers within an educational institution. It features a role-based access system for admins, teachers, and students, each with specific functionalities.

### **Key Features:**
**1. User Roles and Authentication:**
- **Students**: Can request appointments with teachers, view their appointments, and send messages to teachers. Their registration needs admin approval.
- **Teachers**: Can view and manage their appointments, approve or cancel appointments, and respond to student messages.
- **Admins**: Can manage user registrations, approve or reject student registration requests, and manage teacher records.

**2. Firebase Integration:**
- **Authentication:** Uses Firebase Authentication for secure login and registration processes.
- **Firestore Database:** Manages user roles, appointment records, and messages, ensuring real-time updates and data persistence.

**3. Logging and Session Management:**
- Tracks user actions for debugging and monitoring purposes.
- Utilizes Flask sessions to manage user login states and ensure secure access to different parts of the application.

### **Dependencies:**
**Python:**
- Minimum Python 3.6 and above is required (3.10 preferred).
- Flask Python module.
- Firebase-admin module.
- Must properly include Firebase configs and setup serviceAccount.json.

**Firebase:**
- Must properly setup Firebase account.
- Must properly setup Firestore database.
- Must have Service Account Key.
- Must generate Firebase config properly by referring [Firebase API](https://firebase.google.com/docs/reference/admin/python).
- Must have Authentication setup and users with valid roles such as "student", "teacher" or "admin" initially.

### **Installation:**
- Simply download the source code.
- Have your *own Firebase account* setup properly and fill the details inside **main.py** with your Firebase account config.
- Generate private key from account settings in Firebase and paste them in **serviceAccount.json**.
- Create some users with roles as "student", "teacher" and "admin" to get started.
- Check dependencies for modules and start the Python Flask server by running **main.py**.
- Go to [localhost](localhost:5000) and start using the application.

## Thank you
Happy Coding!