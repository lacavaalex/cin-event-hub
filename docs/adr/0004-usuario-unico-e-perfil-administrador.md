# ADR — Uma entidade usuario com perfil administrativo

- **Estado:** Aceita (documentada retrospectivamente)
- **Data de registro:** 2026-11-27
- **Data original da decisão:** não identificada com segurança no histórico consultado
- **Base de análise:** commit `036c3481d0dba6901c92df50311ac396f4f0682a`

## Contexto

O modelo do domínio representa o administrador como um tipo de usuário, sem necessidade de manter uma tabela própria de administradores. O relacionamento de cadastro de eventos também deve apontar para o usuário responsável.

## Decisão

Armazenar usuários em `usuario` e distinguir administradores pelo atributo booleano `is_admin`. `events.admin_id` referencia `usuario.id_usuario` e aceita nulo para eventos que não foram cadastrados manualmente por um administrador.

## Alternativas consideradas

- **Tabela `admins` independente:** duplicaria a identidade e exigiria sincronização entre usuário e administrador.
- **Tabela por papel/perfil:** seria mais flexível para autorização complexa, mas não é necessária para os perfis implementados atualmente.

## Consequências

Há uma única fonte de identidade no banco e a API verifica o perfil administrativo no momento de autorizar a requisição. O booleano é simples, mas não representa uma política RBAC completa com permissões finas. Não promover automaticamente um usuário comum durante o seed evita uma elevação de privilégio acidental.

## Evidências na implementação

`database/001_schema.sql`, `backend/app/models/user.py`, `backend/app/services/auth_service.py`, `backend/app/core/deps.py` e `backend/app/main.py`.
