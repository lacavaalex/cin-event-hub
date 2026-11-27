# syntax=docker/dockerfile:1
#
# Dockerfile do FRONTEND (React + Vite).
#
# Build em DUAS etapas (multi-stage):
#   1) "build"  -> usa Node para instalar dependências e gerar os arquivos
#                  estáticos finais (HTML/CSS/JS) com `vite build`.
#   2) "runtime"-> usa Nginx, um servidor web bem mais leve que Node, só
#                  para SERVIR esses arquivos já prontos.
# Resultado: a imagem final não carrega o Node.js nem o node_modules
# inteiro (centenas de MB) — só os arquivos estáticos + o Nginx.

# ---------- Etapa 1: build ----------
FROM node:22-slim AS build

WORKDIR /app

# Mesma lógica de cache do Dockerfile do backend: copiar só os arquivos de
# dependência primeiro para reaproveitar a camada do `npm ci` entre builds.
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

# IMPORTANTE sobre o Vite: variáveis VITE_* (ex.: VITE_API_URL) são
# "queimadas" no JavaScript DURANTE o build, não lidas em tempo de
# execução como no backend. Por isso o docker-compose.yml passa
# VITE_API_URL como "build arg" (ARG/--build-arg), e não só como
# "environment" do container — se fosse só environment, o navegador do
# usuário (que já recebeu o JS pronto) nunca veria esse valor.
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build
# Resultado: a pasta /app/dist com HTML/CSS/JS estáticos.

# ---------- Etapa 2: runtime (serve o que foi buildado) ----------
FROM nginx:1.27-alpine AS runtime

# Config customizada do Nginx (ver nginx.conf ao lado): necessária porque
# este é um SPA com rotas dinâmicas no client (react-router-dom) — sem
# isso, atualizar a página em "/eventos/5" devolveria 404 do Nginx, já
# que esse caminho não existe como arquivo real no disco.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia só o resultado do build da etapa anterior — nada de Node aqui.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
