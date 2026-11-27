# ADR — Separar a interface React da API REST

- **Estado:** Aceita (documentada retrospectivamente)
- **Data de registro:** 2026-11-27
- **Data original da decisão:** não identificada com segurança no histórico consultado
- **Base de análise:** commit `036c3481d0dba6901c92df50311ac396f4f0682a`

## Contexto

A aplicação precisa disponibilizar uma experiência pública e uma área administrativa, enquanto a lógica de negócio e a persistência devem permanecer no backend. A interface usa navegação client-side e precisa consumir a API por HTTP.

## Decisão

Manter o frontend como SPA em React, com React Router, consumindo uma API REST FastAPI por HTTP/JSON. No desenvolvimento, Vite serve a SPA; na imagem de frontend, Nginx serve os arquivos estáticos gerados pelo build.

## Alternativas consideradas

- **Templates renderizados no servidor:** simplificariam algumas telas, mas não correspondem à estrutura React já adotada.
- **Aplicação desktop ou cliente móvel:** não é necessária para o escopo atual e exigiria outro canal de distribuição.

## Consequências

A interface e a API podem evoluir separadamente e a API pode ser testada sem a interface. Isso exige configurar URL da API e CORS corretamente; o valor `VITE_API_URL` é incorporado no build do Vite. O CORS atual usa origem ampla e precisa ser restringido antes da produção.

## Evidências na implementação

`frontend/package.json`, `frontend/src/App.jsx`, `frontend/src/services/`, `frontend/Dockerfile`, `frontend/nginx.conf`, `backend/app/main.py` e `backend/app/api/`.
