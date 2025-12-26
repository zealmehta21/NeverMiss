# Database Setup Instructions

## Creating the Users Table in Supabase

**IMPORTANT:** You need to run the SQL script directly in Supabase to create the database tables. The SQL file is just code - you must execute it in Supabase SQL Editor.

### Step-by-Step Instructions

1. **Open Supabase Dashboard**
   - Go to [supabase.com](https://supabase.com)
   - Sign in to your account
   - Open your project

2. **Navigate to SQL Editor**
   - Click **SQL Editor** in the left sidebar
   - Click **New Query** button (or use an existing query tab)

3. **Copy the SQL Schema**
   - Open `supabase_schema.sql` from your NeverMiss folder
   - Select and copy ALL the contents of the file

4. **Paste and Run**
   - Paste the SQL code into the SQL Editor
   - Click the **Run** button (or press `Ctrl+Enter`)
   - Wait for execution to complete

5. **Verify Success**
   - You should see "Success. No rows returned" - this is correct!
   - The tables are created even if no rows are returned

6. **Verify Tables Created**
   - Click **Table Editor** in the left sidebar
   - You should now see **three tables**:
     - ✅ `users` - Stores user credentials (email, password hash)
     - ✅ `tasks` - Stores user tasks
     - ✅ `transcripts` - Stores user input history
   - If you don't see the tables, refresh the page

### What the Schema Creates

The `supabase_schema.sql` file creates:

1. **users table**
   - `id` (UUID, Primary Key)
   - `email` (Text, Unique)
   - `password_hash` (Text, for bcrypt hashed passwords)
   - `created_at` (Timestamp)
   - `updated_at` (Timestamp)

2. **tasks table**
   - References `users(id)` via foreign key
   - Stores all user tasks with priorities, due dates, status, etc.

3. **transcripts table**
   - References `users(id)` via foreign key
   - Stores user input history

### Troubleshooting

**Problem: "Can't see users table"**

**Solutions:**
- Make sure you actually ran the SQL script (clicked Run)
- Refresh the Table Editor page
- Check if there were any errors in the SQL Editor
- Try running the SQL script again

**Problem: "Table already exists" errors**

**Solutions:**
- The script uses `CREATE TABLE IF NOT EXISTS` so it's safe to run multiple times
- If you see this error, the tables already exist - that's fine!
- Just verify they exist in Table Editor

**Problem: "Foreign key constraint" errors**

**Solutions:**
- Make sure you're running the complete SQL script
- The `users` table must be created before `tasks` and `transcripts`
- Run the entire script at once, don't run parts separately

### Important Notes

- ✅ **No Git Commit Needed**: You don't need to commit SQL changes to Git
- ✅ **Run Directly in Supabase**: SQL scripts are executed directly in Supabase SQL Editor
- ✅ **Safe to Re-run**: The script uses `IF NOT EXISTS` so it's safe to run multiple times
- ✅ **One-Time Setup**: You only need to run this once per Supabase project

### After Setup

Once the tables are created:
1. Your app can now create users, tasks, and transcripts
2. Users can sign up and their credentials will be stored in the `users` table
3. All passwords are hashed with bcrypt before storage
4. Tasks and transcripts are linked to users via foreign keys

---

**Need Help?**
- Check `RUN_INSTRUCTIONS.md` for complete setup instructions
- Verify your Supabase credentials in `.env` file
- Make sure your Supabase project is active and not paused

