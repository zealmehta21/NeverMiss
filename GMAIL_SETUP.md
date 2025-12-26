# How to Set Up Gmail App Password for SMTP

**IMPORTANT:** You cannot use your regular Gmail password for SMTP. You need to generate an **App Password**.

## Step-by-Step Instructions

### 1. Enable 2-Step Verification (if not already enabled)

1. Go to your [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **2-Step Verification**
3. Follow the prompts to enable it (if not already enabled)

### 2. Generate App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **App passwords**
   - If you don't see this option, make sure 2-Step Verification is enabled first
3. Select "Mail" as the app
4. Select "Other (Custom name)" as the device
5. Type "NeverMiss" or any name you prefer
6. Click **Generate**
7. Google will show you a 16-character password like: `abcd efgh ijkl mnop`
8. **Copy this password** (you won't be able to see it again!)

### 3. Update Your .env File

Open your `.env` file and replace `YOUR_GMAIL_APP_PASSWORD_HERE` with the 16-character App Password (remove spaces):

```env
SMTP_PASSWORD=abcdefghijklmnop
```

### Alternative: Use a Different Email Provider

If you prefer not to use Gmail, you can use other email providers:

- **Outlook/Hotmail**: `smtp-mail.outlook.com` (port 587)
- **Yahoo**: `smtp.mail.yahoo.com` (port 587)
- **Custom SMTP**: Use your own SMTP server settings

Just update `SMTP_SERVER` and `SMTP_PORT` in your `.env` file accordingly.

## Testing

After setting up, you can test if email works by:
1. Running the app: `streamlit run app.py`
2. Creating a task
3. Checking if you receive an email notification

If you encounter issues, check:
- App Password is correct (no spaces, all 16 characters)
- 2-Step Verification is enabled
- You're using the App Password, not your regular password
