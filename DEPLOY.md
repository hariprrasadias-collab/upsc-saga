# Deployment Guide

This application is containerized with Docker, making it easy to deploy to any cloud provider or Virtual Private Server (VPS).

## Option 1: Deploy to a VPS (DigitalOcean, Linode, AWS EC2) - Recommended

This is the most robust method for 24/7 hosting.

1.  **Get a VPS**: Rent a small server (e.g., Ubuntu 22.04) from a provider like DigitalOcean or Hetzner.
2.  **Install Docker**: SSH into your server and install Docker and Docker Compose.
    ```bash
    sudo apt update
    sudo apt install docker.io docker-compose-v2
    ```
3.  **Clone the Repository**:
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```
4.  **Set Environment Variables**:
    Create a `.env` file in the root directory:
    ```bash
    nano .env
    ```
    Add your keys:
    ```
    GEMINI_API_KEY=your_actual_gemini_key
    SECRET_KEY=generate_a_random_secret_string
    ```
5.  **Run the Application**:
    ```bash
    docker compose up -d --build
    ```
    Your app will be available at `http://<your-server-ip>`.

## Option 2: Deploy to Render.com (Free Tier available)

Render can build your Docker containers automatically.

1.  **Backend**:
    *   Create a new **Web Service**.
    *   Connect your GitHub repository.
    *   Select the `backend` directory as the **Root Directory**.
    *   Runtime: **Docker**.
    *   Add Environment Variables: `GEMINI_API_KEY` and `SECRET_KEY`.
2.  **Frontend**:
    *   Create a new **Static Site** (if just static) or another **Web Service** (if using the Dockerfile).
    *   If using the Dockerfile: Select `frontend` as Root Directory, Runtime: Docker.
    *   **Important**: You will need to update the `vite.config.ts` in the frontend to point to your deployed Backend URL instead of `localhost`.

## Option 3: Local 24/7 (Home Server)

If you have a Raspberry Pi or an old laptop:

1.  Install Docker Desktop or Docker Engine.
2.  Run `docker compose up -d` in the project root.
3.  Use `cloudflared` (Cloudflare Tunnel) to expose it securely without port forwarding.
