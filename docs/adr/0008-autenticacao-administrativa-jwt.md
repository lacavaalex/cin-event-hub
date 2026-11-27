# ADR — Autenticar administradores com senha bcrypt e token JWT

- **Estado:** Aceita (documentada retrospectivamente)
- **Data de registro:** 2026-11-27
- **Data original da decisão:** não identificada com segurança no histórico consultado
- **Base de análise:** commit `036c3481d0dba6901c92df50311ac396f4f0682a`

## Contexto

As rotas administrativas precisam distinguir administradores de usuários comuns, proteger operações de escrita e não manter senhas em texto puro. O frontend precisa manter a sessão entre navegações da SPA.

## Decisão

Armazenar hash bcrypt em `usuario.senha_hash`, emitir JWT assinado com o algoritmo configurado (padrão HS256) após login válido e exigir `Authorization: Bearer` nas rotas administrativas. O backend consulta novamente o usuário no banco e exige `is_admin = TRUE` a cada requisição protegida. A chave secreta deve ter ao menos 32 caracteres; a expiração padrão é de 60 minutos.

## Alternativas consideradas

- **Sessão server-side:** seria uma opção válida, mas exigiria armazenamento e gerenciamento de sessão.
- **Autenticar apenas no frontend:** não protegeria os endpoints contra chamadas diretas.
- **Confiar somente nas claims do token sem consultar o banco:** manteria permissões antigas após um usuário perder o perfil administrativo.

## Consequências

As rotas administrativas validam a identidade e o perfil atuais no banco. O frontend guarda o token em `localStorage`, o que exige atenção a XSS e à proteção da aplicação. A autenticação de aluno não está concluída: favoritos recebem `X-User-Id`, e o serviço frontend atual usa valor estático; esse cabeçalho não deve ser tratado como autenticação segura.

## Evidências na implementação

`backend/app/core/security.py`, `backend/app/core/deps.py`, `backend/app/services/auth_service.py`, `backend/app/api/auth/router.py`, `backend/app/api/eventos/router.py` e `frontend/src/contexts/AuthContext.jsx`.
