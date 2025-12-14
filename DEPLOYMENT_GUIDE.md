# Deployment Guide: Free 24/7 Hosting

This guide explains how to deploy the **UPSC Saga** application for free using **Fly.io** (Backend) and **Vercel** (Frontend).

## Architecture
- **Backend**: Hosted on Fly.io (Free Tier). Uses a persistent volume to store the SQLite database (`upsc_saga.db`).
- **Frontend**: Hosted on Vercel (Free Tier). Connects to the backend via API.

---

## Part 1: Backend Deployment (Fly.io)

We use Fly.io because it supports persistent storage volumes, which are required for the SQLite database.

### Prerequisites
1. Install `flyctl` (Fly.io CLI): https://fly.io/docs/hands-on/install-flyctl/
2. Sign up for a Fly.io account (requires a credit card for identity verification, but the free tier is sufficient).

### Steps

1. **Login to Fly.io**
   ```bash
   fly auth login
   ```

2. **Navigate to the Backend Directory**
   ```bash
   cd backend
   ```

3. **Initialize the App**
   The `fly.toml` file is already created. You need to verify the app name is unique.
   Open `backend/fly.toml` and change the `app = "..."` line to a unique name, e.g., `upsc-saga-backend-yourname`.

4. **Create the Volume**
   This creates a 1GB persistent disk for your database in the `iad` (Ashburn, Virginia) region. You can change the region code if desired.
   ```bash
   fly volume create sqlite_data --region iad --size 1
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

6. **Get the Backend URL**
   Once deployed, Fly.io will give you a URL (e.g., `https://upsc-saga-backend-yourname.fly.dev`).
   **Copy this URL.** You will need it for the frontend.

---

## Part 2: Frontend Deployment (Vercel)

We use Vercel for the frontend as it is optimized for React/Vite applications.

### Prerequisites
1. A GitHub account (recommended) or Vercel CLI.

### Steps (via GitHub Integration - Recommended)

1. **Push your code to GitHub.**
2. Log in to [Vercel](https://vercel.com).
3. Click **"Add New..."** -> **"Project"**.
4. Import your GitHub repository.
5. **Configure Project**:
   - **Root Directory**: Click "Edit" and select `frontend`.
   - **Environment Variables**:
     - Name: `VITE_API_BASE_URL`
     - Value: `https://upsc-saga-backend-yourname.fly.dev` (The URL from Part 1, without a trailing slash).
6. Click **Deploy**.

### Steps (via Vercel CLI)

1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Deploy:
   ```bash
   vercel
   ```
4. Follow the prompts. When asked for environment variables, add:
   - `VITE_API_BASE_URL`: Your backend URL.

---

## Verification

1. Open your Vercel URL.
2. The app should load.
3. Check the "Dashboard" to see if data is loading from the backend.
4. Try completing a task to ensure the database is writable.

## Troubleshooting

- **Database Errors**: Check the Fly.io logs: `fly logs -a your-app-name`.
- **CORS Errors**: Ensure your backend URL in Vercel is correct (starts with `https://`). The backend is configured to allow all origins (`*`), so CORS should not be an issue.
- **Persistence**: If your data disappears after a restart, ensure the `fly.toml` has the `[mounts]` section correctly configured and that `DATABASE_PATH` is set to `/data/upsc_saga.db`.
