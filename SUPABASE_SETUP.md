# How to Enable Google Sign-In in Supabase

Follow these steps to configure Google Authentication for your application.

## Step 1: Set up Google Cloud Platform (GCP)

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a **New Project** (e.g., "Coast to Coast Journeys").
3.  **OAuth Consent Screen**:
    *   Navigate to **APIs & Services > OAuth consent screen**.
    *   Select **External** user type and click **Create**.
    *   Fill in the required fields (App name, User support email, Developer contact email).
    *   Click **Save and Continue** through the steps (you can skip Scopes and Test Users for now, or add your email as a test user).
    *   **Publish App**: Click "Publish App" if in testing mode to avoid "verification required" errors for your own account, or leave in Testing mode and add your email to "Test Users".

4.  **Create Credentials**:
    *   Navigate to **APIs & Services > Credentials**.
    *   Click **Create Credentials** -> **OAuth client ID**.
    *   **Application type**: Select **Web application**.
    *   **Name**: e.g., "Supabase Auth".
    *   **Authorized JavaScript origins**: `https://bcxkjvjchutgfuyklphx.supabase.co` (This is your Supabase URL domain).
    *   **Authorized redirect URIs**: `https://bcxkjvjchutgfuyklphx.supabase.co/auth/v1/callback` (This is critical).
    *   Click **Create**.
    *   **Copy** the `Client ID` and `Client Secret`.

## Step 2: Configure Supabase

1.  Go to your [Supabase Dashboard](https://supabase.com/dashboard/project/bcxkjvjchutgfuyklphx).
    *   *(Note: The project ID `bcxkjvjchutgfuyklphx` was taken from your `supabase-client.js`. Ensure you are in the correct project.)*
2.  Navigate to **Authentication > Providers**.
3.  Click on **Google** and toggle it **Enable**.
4.  Paste the **Client ID** and **Client Secret** you copied from Google Cloud.
5.  Click **Save**.

## Step 3: Verify Redirect URL

1.  In Supabase, under **Authentication > URL Configuration**, ensure your Site URL is set correctly (usually `http://localhost:5000` or wherever you are hosting locally).
2.  Add `http://localhost:5000/auth.html` and `http://127.0.0.1:5000/auth.html` to the **Redirect URLs** allowlist if not present.

## Step 4: Test Login

Go back to your application login page and click "Sign in with Google". It should now work!
