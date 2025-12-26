# Custom Authentication System Update

## Changes Made

### 1. Created Users Table ✅

**File Updated**: `supabase_schema.sql`

Created a custom `users` table to store user credentials:
```sql
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Changes**:
- Updated `tasks` table to reference `users(id)` instead of `auth.users(id)`
- Updated `transcripts` table to reference `users(id)` instead of `auth.users(id)`
- Removed RLS policies (no longer needed with custom auth)

### 2. Added Password Hashing ✅

**File Updated**: `requirements.txt`

- Added `bcrypt>=4.0.0` for secure password hashing

**Security**:
- Passwords are hashed using bcrypt before storage
- Passwords are never stored in plain text
- Uses industry-standard bcrypt hashing algorithm

### 3. Rewrote Authentication Functions ✅

**File Updated**: `database.py`

**New Functions**:
- `hash_password(password: str) -> str` - Hashes passwords using bcrypt
- `verify_password(password: str, password_hash: str) -> bool` - Verifies passwords
- `create_user(email: str, password: str) -> Dict` - Creates user in users table
- `sign_in(email: str, password: str) -> Dict` - Verifies credentials and stores in session
- `sign_out()` - Clears session state
- `get_current_user()` - Retrieves user from session state
- `update_user_password(user_id: str, new_password: str)` - Updates password
- `reset_password(email: str, new_password: str)` - Resets password by email

**Key Changes**:
- No longer uses Supabase Auth
- Uses Streamlit session state for authentication
- All passwords are hashed before storage
- Password verification uses bcrypt comparison

### 4. Simplified Password Reset ✅

**File Updated**: `pages/5_Reset_Password.py`

**Before**: Sent email with reset link
**Now**: Simple form with:
- Email field
- New password field
- Confirm password field
- Reset button

**How it works**:
1. User enters email, new password, and confirms password
2. System directly updates the password in the database
3. User is redirected to login page
4. User can log in with new password

**For logged-in users**: Can change password directly (no email needed)

### 5. Updated Database Schema ✅

You need to run the updated `supabase_schema.sql` in your Supabase SQL Editor to:
1. Create the `users` table
2. Update foreign key references in `tasks` and `transcripts` tables
3. Remove old RLS policies

---

## Setup Instructions

### Step 1: Update Database Schema

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Open the updated `supabase_schema.sql` file
4. **Important**: If you have existing data, you may need to:
   - Backup your data first
   - Drop existing foreign key constraints
   - Update user_id references to point to your new users table
5. Run the SQL script

### Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install `bcrypt` for password hashing.

### Step 3: Test the System

1. **Sign Up**: Create a new account
   - Credentials are saved in the `users` table
   - Password is hashed before storage

2. **Sign In**: Log in with your credentials
   - Credentials are verified against the `users` table
   - Session is stored in Streamlit session state

3. **Reset Password**: Test password reset
   - Enter email, new password, confirm password
   - Password is updated directly in the database
   - Redirect to login page

---

## Security Features

✅ **Password Hashing**: All passwords are hashed using bcrypt before storage
✅ **No Plain Text**: Passwords are never stored in plain text
✅ **Session Management**: User sessions are managed via Streamlit session state
✅ **Email Uniqueness**: Email addresses are unique in the database
✅ **Direct Updates**: Password reset directly updates database (no email links needed)

---

## Migration Notes

If you have existing users in Supabase Auth:
- You'll need to migrate them to the new `users` table
- You cannot retrieve their passwords (they're hashed in Supabase Auth)
- Users will need to reset their passwords using the new reset flow

---

## API Changes

### Before (Supabase Auth):
```python
supabase.auth.sign_up({...})
supabase.auth.sign_in_with_password({...})
supabase.auth.get_user()
```

### After (Custom Auth):
```python
create_user(email, password)  # Stores in users table
sign_in(email, password)  # Verifies against users table
get_current_user()  # Returns from session state
```

---

## Testing Checklist

- [ ] Install bcrypt: `pip install bcrypt`
- [ ] Run updated schema in Supabase
- [ ] Test user signup
- [ ] Test user login
- [ ] Test password reset (not logged in)
- [ ] Test password change (logged in)
- [ ] Verify tasks and transcripts still work
- [ ] Verify user can log out and log back in

