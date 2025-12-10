# Secure Feedback Portal - Setup & Run Guide

## Project Overview
A complete full-stack feedback system with public feedback submission and secure admin dashboard.

## Tech Stack
- **Frontend**: Single `index.html` with vanilla JavaScript, HTML, and CSS
- **Backend**: Python Flask application (`app.py`)
- **Database**: SQLite (`feedback.db` - auto-created)

## Project Structure
```
recreate/
├── backend/
│   └── app.py
├── frontend/
│   └── index.html
└── feedback.db (auto-created on first run)
```

## Prerequisites
- Python 3.7+
- Flask (`pip install flask`)

## Installation & Setup

### 1. Install Dependencies
```bash
pip install flask
```

### 2. Navigate to the Backend Directory
```bash
cd backend
```

### 3. Run the Flask Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Features

### For Normal Users
1. **Home Page** (`http://localhost:5000/`)
   - Clean, responsive interface
   - "Give Feedback" button to open the feedback form
   - Form is dynamically generated from field configuration
   - Fields: Name, Email, Rating (1-5), Comments
   - After submission, a success message is displayed

2. **Admin Login Button**
   - Located in the top-right navbar
   - Links to `/admin/login`

### For Admins
1. **Admin Login** (`http://localhost:5000/admin/login`)
   - **Default Credentials:**
     - Username: `admin`
     - Password: `admin123`
   - ⚠️ **Change these in production!** (See `app.py` lines for `ADMIN_USERNAME` and `ADMIN_PASSWORD`)

2. **Admin Dashboard** (`http://localhost:5000/admin/dashboard`)
   - Only accessible after successful login
   - Displays all feedback entries in a table
   - Shows: ID, Name, Email, Rating, Comments, Submission Time
   - **Logout Button** in the top-right to clear session

### Security Features
- Session-based authentication for admin
- Feedback data is only visible after admin login
- Anonymous users cannot access the dashboard
- Form validation on both frontend and backend

## API Endpoints

### Public Endpoints
- **GET `/`** - Serve the main feedback portal
- **POST `/api/feedback`** - Submit feedback (JSON)
  - Request body:
    ```json
    {
      "name": "string",
      "email": "string",
      "rating": number (1-5),
      "comments": "string (optional)"
    }
    ```
  - Returns: `{ "message": "Feedback submitted successfully" }`

### Admin Endpoints
- **GET `/admin/login`** - Display admin login form
- **POST `/admin/login`** - Process admin login
- **GET `/admin/dashboard`** - Display feedback dashboard (requires login)
- **GET `/admin/logout`** - Logout and clear session

## Database Schema

### `feedback` table
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    rating INTEGER NOT NULL,
    comments TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Customization

### Change Admin Credentials
Edit `backend/app.py` (lines ~17-18):
```python
ADMIN_USERNAME = 'your_username'
ADMIN_PASSWORD = 'your_password'
```

### Modify Feedback Form Fields
Edit `frontend/index.html` (line ~284):
```javascript
const feedbackFields = [
    { name: "field_name", label: "Field Label", type: "text/email/number/textarea", required: true }
];
```

### Change Flask Port
Edit `backend/app.py` (last line):
```python
app.run(debug=True, port=8000)  # Change 5000 to desired port
```

## Testing the Application

### Test Feedback Submission
1. Open `http://localhost:5000/`
2. Click "Give Feedback"
3. Fill the form (all required fields marked with *)
4. Click "Submit Feedback"
5. You should see a success message

### Test Admin Access
1. Click "Admin Login" button
2. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
3. You'll be redirected to the dashboard
4. View all submitted feedback in the table
5. Click "Logout" to end the session

### Test Security
1. Try accessing `/admin/dashboard` directly without logging in
   - You should be redirected to the login page
2. Submit feedback as a normal user
3. Verify the feedback appears in the admin dashboard
4. Try to access admin endpoints as an anonymous user
   - You cannot view any feedback data

## Troubleshooting

### Port Already in Use
If port 5000 is already in use:
1. Edit `backend/app.py` (last line) and change the port number
2. Or kill the process using port 5000

### Database Issues
If `feedback.db` is corrupted:
1. Delete `feedback.db`
2. Restart the application
3. A new database will be created automatically

### Form Not Loading
1. Clear your browser cache
2. Ensure JavaScript is enabled
3. Check browser console for errors (F12)

## Production Deployment Notes
- Change the Flask `secret_key` (line ~11)
- Change admin credentials
- Set `debug=False` in `app.run()`
- Use a production WSGI server (gunicorn, uWSGI, etc.)
- Store credentials securely (environment variables, etc.)
- Use HTTPS
- Implement rate limiting for API endpoints
- Add password hashing for admin credentials

## License
This project is provided as-is for educational purposes.
