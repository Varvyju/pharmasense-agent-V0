# PharmaSense Agent — Deployment Guide

## Option 1: Railway (Recommended for hackathon — 5 min)

Railway is the fastest. No setup, auto-deploys from GitHub.

### Prerequisites
- Repository pushed to GitHub
- Railway account (free tier: railway.app)

### Steps

1. **Connect GitHub to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "Start a new project"
   - Select "Deploy from GitHub repo"
   - Authorize & select your PharmaSense repo

2. **Create backend service**
   - In Railway dashboard, click "New Service"
   - Select "GitHub repo" → your pharmasense-agent repo
   - Configure:
     - **Root Directory:** `backend`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `PORT=8000` (or let Railway auto-assign)
   - Deploy

3. **Create frontend service**
   - Click "New Service" again
   - Select same repo
   - Configure:
     - **Root Directory:** `frontend`
     - **Build Command:** `npm install && npm run build`
     - **Start Command:** `npm run preview` (or use `serve -s dist -l 3000`)
   - Add environment variable: `VITE_API_URL=https://<backend-service-url>`
   - Deploy

4. **Link services**
   - In backend logs, grab the assigned URL (e.g., `https://pharmasense-backend.railway.app`)
   - Update frontend's `VITE_API_URL` environment variable with this URL
   - Redeploy frontend

5. **Done!** Frontend URL is your public demo link.

---

## Option 2: Docker Compose (Local Testing)

Test everything locally before pushing:

```bash
cd c:\Users\user\Downloads\pharmasense-agent\pharmasense-agent

# Build and start both services
docker-compose up --build

# Access:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000/api/health
```

Stop with `Ctrl+C`.

---

## Option 3: Azure Container Instances (Enterprise)

For persistent hosting on Azure:

### Prerequisites
- Azure account + subscription
- Docker image pushed to Azure Container Registry (ACR)

### Steps

1. **Build and push backend image**
   ```bash
   az acr build `
     --registry <your-acr-name> `
     --image pharmasense-backend:latest `
     --file backend/Dockerfile `
     c:\Users\user\Downloads\pharmasense-agent\pharmasense-agent\backend
   ```

2. **Build and push frontend image**
   ```bash
   az acr build `
     --registry <your-acr-name> `
     --image pharmasense-frontend:latest `
     --file frontend/Dockerfile `
     --build-arg VITE_API_URL=https://<backend-ip>:8000 `
     c:\Users\user\Downloads\pharmasense-agent\pharmasense-agent\frontend
   ```

3. **Deploy backend container**
   ```bash
   az container create `
     --resource-group <your-rg> `
     --name pharmasense-backend `
     --image <acr-name>.azurecr.io/pharmasense-backend:latest `
     --registry-login-server <acr-name>.azurecr.io `
     --registry-username <username> `
     --registry-password <password> `
     --ports 8000 `
     --environment-variables PORT=8000
   ```

4. **Deploy frontend container**
   ```bash
   az container create `
     --resource-group <your-rg> `
     --name pharmasense-frontend `
     --image <acr-name>.azurecr.io/pharmasense-frontend:latest `
     --registry-login-server <acr-name>.azurecr.io `
     --registry-username <username> `
     --registry-password <password> `
     --ports 5173 `
     --environment-variables VITE_API_URL=http://<backend-container-ip>:8000
   ```

5. **Access** via the Azure portal (Container Instances → your service → IP address).

---

## Quick Verification

After deployment, test the API health endpoint:

```bash
curl https://<your-backend-url>/api/health
```

Should return:
```json
{
  "status": "ok",
  "patients_loaded": 28,
  "kb_entries_loaded": 13
}
```

If patients/KB are not loaded, check that the Docker volume includes the `/data` folder.
