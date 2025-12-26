# Supabase Auth Migration - Setup Instructions

## ✅ Changes Completed

All code has been updated to use Supabase Auth instead of custom authentication. Here's what changed:

### 1. Database Schema (`supabase_schema.sql`)
- ✅ Removed custom `users` table
- ✅ Updated `tasks` and `transcripts` to reference `auth.users(id)`
- ✅ Added RLS policies for secure data access
- ✅ Set `user_id` defaults to `auth.uid()`

### 2. Authentication (`database.py`)
- ✅ Removed bcrypt password hashing
- ✅ Using Supabase Auth (`sign_up`, `sign_in_with_password`)
- ✅ Storing session tokens: `sb_access_token`, `sb_refresh_token`, `sb_user`
- ✅ Created authenticated client with JWT token for RLS

### 3. Database Operations
- ✅ Removed `user_id` parameter from `create_task()` - RLS handles it
- ✅ Removed `user_id` parameter from `save_transcript()` - RLS handles it
- ✅ Removed `user_id` filtering from queries - RLS ensures user isolation
- ✅ All operations use authenticated client with JWT

### 4. Pages Updated
- ✅ `pages/3_Signup.py` - Uses `sign_up()` with email confirmation handling
- ✅ `pages/4_Login.py` - Uses `sign_in()` (already correct)
- ✅ `pages/5_Reset_Password.py` - Uses `reset_password_for_email()`
- ✅ `pages/2_Main_App.py` - Removed all `user_id` parameters from DB calls

### 5. Dependencies
- ✅ Removed `bcrypt` from `requirements.txt`

---

## 🔧 What You Need to Do

### Step 1: Update Supabase Database Schema

**IMPORTANT:** You must run the new SQL schema in Supabase to switch from custom auth to Supabase Auth.

1. Go to your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Copy the contents of `supabase_schema.sql`
4. Paste and run it

**⚠️ WARNING:** This will DROP your existing `users`, `tasks`, and `transcripts` tables if they exist. If you have existing data:

- **Option A**: Export your data first, run the schema, then re-import
- **Option B**: Manually update the schema to preserve data (more complex)

### Step 2: Configure Supabase Auth Settings

1. **Disable Email Confirmation (Recommended for Development)**
   - Go to **Authentication > Settings** in Supabase Dashboard
   - Under **Email Auth**, toggle **"Enable email confirmations"** to OFF
   - This allows immediate login after signup

2. **Set Up Redirect URLs (For Password Reset)**
   - Go to **Authentication > URL Configuration**
   - Add redirect URLs:
     - `http://localhost:8501/*` (for local development)
     - Your production URL if applicable
   - This is needed for password reset links to work

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** bcrypt is no longer needed and has been removed.

### Step 4: Test the Application

1. **Run the app:**
   ```bash
   streamlit run app.py
   ```

2. **Test signup:**
   - Go to signup page
   - Create a new account
   - Should log in automatically (if email confirmation is disabled)

3. **Test login:**
   - Log out
   - Log back in with your credentials

4. **Test password reset:**
   - Click "Forgot password?"
   - Enter your email
   - Check your email for reset link
   - Follow the link to reset password

---

## 🔑 How It Works Now

### Authentication Flow

1. **Sign Up:**
   - User signs up via `sign_up(email, password)`
   - Supabase Auth creates user in `auth.users`
   - Session tokens stored in Streamlit session state
   - User is automatically logged in

2. **Sign In:**
   - User signs in via `sign_in(email, password)`
   - Supabase Auth verifies credentials
   - Session tokens stored in session state
   - User is authenticated

3. **Database Operations:**
   - All DB operations use `get_authenticated_client()`
   - Access token is applied to enable RLS
   - RLS policies ensure users only see their own data
   - No need to pass `user_id` - RLS handles it automatically

### Row Level Security (RLS)

RLS policies ensure:
- Users can only SELECT their own tasks/transcripts
- Users can only INSERT tasks/transcripts with their own user_id
- Users can only UPDATE/DELETE their own tasks
- `auth.uid()` automatically fills in `user_id` on INSERT

---

## ⚠️ Important Notes

### Email Confirmation

- If email confirmation is **enabled** in Supabase:
  - Users must confirm email before logging in
  - Signup will show "Check your email to confirm"
  
- If email confirmation is **disabled**:
  - Users can log in immediately after signup
  - Recommended for development/testing

### Password Reset

- Uses Supabase's built-in password reset flow
- Sends email with reset link
- User clicks link → redirected to Supabase → can set new password
- Requires redirect URLs to be configured in Supabase dashboard

### Session Management

- Session tokens stored in Streamlit session state:
  - `sb_access_token` - JWT token for authenticated requests
  - `sb_refresh_token` - Token for refreshing session
  - `sb_user` - User ID and email
  
- Sessions persist across page reruns
- Logout clears all session data

---

## 🐛 Troubleshooting

### "RLS policy violation" errors
- Make sure RLS policies are created (run the SQL schema)
- Verify access token is being applied to requests
- Check that user is logged in (has session tokens)

### "User not authenticated" errors
- Check that `sb_access_token` exists in session state
- Verify user logged in successfully
- Try logging out and logging back in

### Password reset not working
- Check redirect URLs are configured in Supabase
- Verify email is sent (check spam folder)
- Make sure you're clicking the link from the email

### Can't see data after migration
- If you had existing data with custom auth, it's been dropped
- You'll need to create new accounts and tasks
- Or manually migrate data from old schema

---

## 📝 Summary

✅ All authentication now uses Supabase Auth
✅ RLS ensures secure data access
✅ No more bcrypt or custom password hashing
✅ Simpler code - no need to pass user_id everywhere
✅ Better security - managed by Supabase

**Next Steps:**
1. Run the new SQL schema in Supabase
2. Configure Supabase Auth settings
3. Test the application
4. Enjoy simplified authentication! 🎉

