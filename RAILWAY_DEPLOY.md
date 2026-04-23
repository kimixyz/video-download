# Railway Deployment

## Recommended topology

- Frontend stays on Vercel.
- Backend runs on Railway from `video-download/backend`.
- Railway is the only production API backend.
- Frontend uses `NEXT_PUBLIC_API_BASE_URL` to call the Railway backend in production.

## Backend deployment on Railway

1. Create a new Railway project.
2. Connect this repository.
3. Set the service root directory to `backend`.
4. If Railway asks how to build, prefer the `Dockerfile` inside `backend`.
5. If you do not use Docker, Railway can still install from `requirements.txt` and start from `Procfile`.
6. Use this start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

6. Add environment variables:

```bash
FRONTEND_URL=https://your-frontend-domain.com
```

7. Expose the service to generate a public Railway domain.
8. After deployment, verify:

```bash
GET /healthz
POST /api/parse
GET /api/download
```

## Frontend deployment on Vercel

Add this environment variable in Vercel:

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend.up.railway.app
```

This variable is required in production because the Vercel-side Python API has been removed.

## Local development

- Keep `NEXT_PUBLIC_API_BASE_URL` unset locally.
- Run the backend on port 8000.
- Run the frontend on port 3000.
- The existing development rewrite in `frontend/next.config.ts` continues to proxy `/api/*` to `http://localhost:8000`.

## Domain and CORS

- Point your public frontend domain to Vercel.
- Keep Railway on its generated domain first, then add a custom API domain later if needed.
- Set `FRONTEND_URL` in Railway to the exact frontend origin, such as `https://video.example.com`.

## Suggested rollout

1. Deploy the backend to Railway and validate `/healthz`.
2. Set `NEXT_PUBLIC_API_BASE_URL` in Vercel.
3. Redeploy the frontend.
4. Test parse and download from the production domain.
5. Keep Vercel responsible only for the frontend build and static delivery.

## If Railway import fails immediately

- This repository is a monorepo, so the Railway service must point to `backend` instead of the repository root.
- Push the latest GitHub commit first. Railway only sees files that are already on GitHub.
- If the service was created against the wrong root, open Railway service settings and change the root directory to `backend`, then redeploy.
- If Railpack still fails, create a fresh service and choose the `Dockerfile` build path from `backend`.