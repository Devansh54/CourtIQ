# CourtIQ — Production Deployment Guide

This guide covers all deployment targets for the CourtIQ Tennis Analytics Platform, ranging from local Docker evaluation to managed cloud hosting.

---

## 1. Local Deployment (Current Environment)

CourtIQ is designed to run locally using Docker for the PostgreSQL 18 database engine and Python for the Streamlit dashboard:

```bash
# 1. Start PostgreSQL 18 container
docker compose up -d

# 2. Seed database schemas and demo fixtures (1 command)
python scripts/seed_demo_data.py

# 3. Launch Streamlit UI
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 2. Free Cloud Hosting: Streamlit Community Cloud

CourtIQ can be deployed for free with zero server maintenance on [Streamlit Community Cloud](https://share.streamlit.io):

1. **Push to GitHub:** Ensure your repository is pushed to your GitHub account (`https://github.com/Devansh54/CourtIQ`).
2. **Deploy via Web UI:**
   - Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
   - Click **"New App"**.
   - Select repository `Devansh54/CourtIQ`, branch `main`, and main file path `app.py`.
3. **Configure Cloud Secrets:**
   In App Settings > Secrets, add:
   ```toml
   COURTIQ_MODE = "DEMO"
   DATABASE_URL = "postgresql+psycopg://<user>:<password>@<remote-postgres-host>:5432/courtiq"
   ```
   *(For free cloud PostgreSQL databases, you can use [Neon.tech](https://neon.tech), [Supabase](https://supabase.com), or [Aiven](https://aiven.io)).*
4. Click **Deploy**. Your app will be live at `https://courtiq.streamlit.app`.

---

## 3. Containerized Cloud Deployment (Render / Railway / AWS / GCP)

Using the included multi-stage [`Dockerfile`](../Dockerfile):

### Render / Railway / Fly.io:
1. Connect your repository to Render/Railway.
2. Choose **Docker** as the environment runtime.
3. Attach a managed PostgreSQL database.
4. Set environment variables:
   - `COURTIQ_MODE=DEMO` (or `LIVE` with `SPORTRADAR_API_KEY`)
   - `DATABASE_URL=postgresql+psycopg://...`
5. Deploy. The platform will automatically build the container and serve on port 8501.

### Build and Run Docker Image Locally:
```bash
# Build the production image
docker build -t courtiq:v1.0.0 .

# Run the container
docker run -p 8501:8501 --env-file .env courtiq:v1.0.0
```

---

## 4. Production Checklist

- [x] Multi-stage `Dockerfile` with non-root security.
- [x] Automated health check (`/_stcore/health`).
- [x] Streamlit toolbars and deploy prompts hidden in production styling.
- [x] Parameterized SQL queries preventing injection vulnerabilities.
- [x] Zero credential leakage in exception tracebacks or logs.
