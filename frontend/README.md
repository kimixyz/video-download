# 视频解析下载 Frontend

Next.js 前端，负责提交视频链接、展示解析结果，并通过后端代理下载视频文件。

## 本地开发

```bash
npm install
npm run dev
```

默认访问 `http://localhost:3000`。本地开发时保持 `NEXT_PUBLIC_API_BASE_URL` 未设置，`next.config.ts` 会把 `/api/*` 代理到 `http://localhost:8000`。

## 生产部署

前端部署到 Vercel，后端部署到 Railway。生产环境必须配置：

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend.up.railway.app
```

更多后端部署步骤见仓库根目录的 `RAILWAY_DEPLOY.md`。

## 常用命令

```bash
npm run lint
npm run test
npm run build
```
