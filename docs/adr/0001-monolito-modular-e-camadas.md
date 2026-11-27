# ADR — Backend como monólito modular organizado em camadas

- **Estado:** Aceita (documentada retrospectivamente)
- **Data de registro:** 2026-11-27
- **Data original da decisão:** não identificada com segurança no histórico consultado
- **Base de análise:** commit `036c3481d0dba6901c92df50311ac396f4f0682a`

## Contexto

O backend concentra autenticação, eventos, favoritos, extração e limpeza de eventos. Essas responsabilidades precisam ser separadas para facilitar manutenção, mas o projeto acadêmico não exige a operação de vários serviços independentes.

A implementação usa um único serviço FastAPI, com routers e schemas na interface HTTP, serviços para regras de negócio, repositórios para acesso a dados e models SQLAlchemy para persistência. O frontend é outro artefato de execução, mas os módulos de backend não são microserviços.

## Decisão

Manter o backend como **monólito modular** com três camadas lógicas: apresentação/API, aplicação/negócio e persistência/dados. Os módulos internos são separados por domínio e responsabilidade, mas são empacotados e executados juntos.

## Alternativas consideradas

- **Microserviços:** aumentariam a autonomia de deploy e escala por domínio, mas adicionariam rede, observabilidade, contratos distribuídos e operação sem necessidade demonstrada pelo escopo atual.
- **Backend sem separação interna:** seria mais simples no início, mas concentraria regras, HTTP e consultas nas mesmas funções e dificultaria os testes.

## Consequências

A solução mantém implantação e operação relativamente simples e permite testar regras de negócio separadas das rotas. Em contrapartida, os módulos compartilham processo, ciclo de vida e escala. A separação em camadas é lógica, não uma fronteira de serviço distribuído.

## Evidências na implementação

`backend/app/api/`, `backend/app/schemas/`, `backend/app/services/`, `backend/app/repositories/`, `backend/app/models/`, `backend/app/database/` e `backend/app/main.py`.
