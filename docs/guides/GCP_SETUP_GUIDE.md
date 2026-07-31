# Google Cloud Platform (GCP) Setup Guide

This guide explains exactly what you need to have and do **before** running the deployment script.

## 1. What You Need (Prerequisites)

To use Google Cloud, you must have:
*   **Google Account**: A standard Gmail or Google Workspace account.
*   **Payment Method**: A credit or debit card.
    *   *Note:* Google asks for this to verify you are human. They offer a **Free Tier** and **$300 free credit** for new users, so you likely won't be charged unless you scale up significantly.
*   **A Project Name**: A unique ID for your app (e.g., `coast-to-coast-app`).

## 2. Step-by-Step Setup (Web Console)

### Step A: Create a Project
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Log in with your Google Account.
3.  Click the **Project Dropdown** (top left, near the logo).
4.  Click **New Project**.
5.  Enter a name (e.g., `coast-to-coast-journeys`).
6.  Click **Create**.
7.  **Important**: Wait a moment, then select your new project from the notification bell or dropdown.

### Step B: Enable Billing
1.  In the Navigation Menu (top left ☰), click **Billing**.
2.  Click **Link a billing account**.
3.  Follow the prompts to add your credit/debit card.
    *   *Why?* Cloud Run requires billing to be enabled to function, even if usage is within free limits.

### Step C: Enable Required APIs
The deployment script tries to do this, but doing it manually ensures smoothness.
1.  In the Search bar at the top, type **"Cloud Run API"** and select it.
    *   Click **Enable**.
2.  Search for **"Cloud Build API"**.
    *   Click **Enable**.
3.  Search for **"Artifact Registry API"**.
    *   Click **Enable**.

## 3. Connect Your Computer (Terminal)

Now that the *cloud* side is ready, connect your *local* machine.

1.  **Install the Google Cloud SDK (gcloud CLI)**:
    *   **Mac (Homebrew)**: Open terminal and run:
        ```bash
        brew install --cask google-cloud-sdk
        ```
    *   **Or Download**: Get the installer from [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install).

2.  **Initialize (Login)**:
    *   Run this command in your terminal:
        ```bash
        gcloud init
        ```
    *   It will open a browser window. **Log in** with the same Gmail account.
    *   It will ask you to **Pick a Project**. Select the specific number corresponding to the project you created in Step A (e.g., `coast-to-coast-journeys`).
    *   (Optional) It might ask for a "zone". You can pick `us-central1-a` (Iowa) or any other.

## 4. Run the Deployment Script

Once `gcloud init` is successful, you are ready!

1.  Make sure you are in your project folder in the terminal.
2.  Run:
    ```bash
    ./deploy.sh
    ```

This script will now automatically:
1.  Detect your Project ID.
2.  Read your local `.env` file for secrets.
3.  Package your app and send it to Google Cloud.
4.  Give you a public URL (e.g., `https://c2c-journeys-xyz-uc.a.run.app`).
