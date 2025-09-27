
# Sistema de Controle de EPIs — Especificação (MVP)

## 1) Escopo resumido
Objetivo: controlar cadastro de EPIs, colaboradores e o empréstimo/devolução de itens.

Perfis de usuário (campo `perfil` em `usuarios` — futura evolução):
- ADMIN / TECNICO_SST / ALMOXARIFE / COLABORADOR

## 2) DER (conceitual simplificado)
Entidades principais:
- **Colaborador**(id, nome, cpf, matrícula, ativo)
- **Epi**(id, código, nome, tamanho, ca_numero, ca_validade, estoque, ativo)
- **Emprestimo**(id, colaborador_id, criado_em, previsao_devolucao)
- **EmprestimoItem**(id, emprestimo_id, epi_id, quantidade, entregue_em, status, devolvido_em?, observacao_devolucao?)

## 3) Diagrama de Casos de Uso
(Imagem enviada pelo solicitante)
![Casos de Uso](/mnt/data/9efae0b7-98c9-4b47-80c5-bc101c5d665d.png)

## 4) Requisitos Funcionais (implementados no MVP)
- RF01 — (parcial) Estrutura preparada; login não obrigatório nesta entrega.
- RF02 — CRUD de colaboradores com validações.
- RF03 — CRUD de EPIs com estoque e CA.
- RF04 — Empréstimo com 1..N itens e baixa automática do estoque.
- RF05 — Devolução total/parcial por item; recomposição do estoque quando **Devolvido**.
- RF06 — Relatório por colaborador com pendências/histórico.
- RF07 — (opcional) Avisos visuais de CA vencido podem ser evoluídos na UI.

## 5) Requisitos Não Funcionais
- Usabilidade: até 3 cliques para registrar empréstimo.
- Segurança: estrutura pronta para autenticação e perfis.
- Desempenho: consultas com índices naturais.
- Manutenibilidade: Django (camadas: models/forms/views/templates).

## 6) Wireframes (mínimos)
Ver README do projeto e telas geradas.

## 7) Regras de Negócio aplicadas
- RB01: `quantidade > 0` em `EmprestimoItem`.
- RB02: Não permite saída se `epi.estoque < quantidade` (validação).
- RB03: Ao **Devolvido** soma ao estoque e registra `devolvido_em`.
- RB04: Se `ca_validade` vencida, pode-se exibir aviso (UI futura).
- RB05: Empréstimo é considerado **FECHADO** quando não há itens pendentes (propriedade `status`).

## 8) Critérios de Aceite (MVP)
- CRUD de usuários (colaboradores), EPIs ✅
- Empréstimo com N itens e baixa de estoque ✅
- Devolução total/parcial e recomposição de estoque ✅
- Listagem de pendências e relatório por colaborador ✅
- Exportação CSV (pode ser adicionada em uma próxima iteração)

