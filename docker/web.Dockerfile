# Dev-mode web container: Vite dev server with HMR. A production image would add
# a `build` stage + nginx; deferred until Phase 6 (deployment).
FROM node:22-slim

WORKDIR /app
COPY web/package.json web/package-lock.json* ./
RUN npm install
COPY web ./

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
