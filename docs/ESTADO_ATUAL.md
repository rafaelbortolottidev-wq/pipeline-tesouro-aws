# Estado Atual — Pipeline Tesouro Direto AWS

**Projeto:** P02 — Pipeline Tesouro Direto AWS  
**Versão:** 1.0  
**Data:** 24/10/2026  
**Status:** Encerrado tecnicamente, com limitação externa documentada.

## 1. Entregas concluídas

- Bronze, Silver e Gold no Amazon S3.
- ETL executado com sucesso no AWS Glue Python Shell.
- Silver: **177.260 registros**.
- Gold: **150 registros**.
- Glue Data Catalog e consultas Athena validados.
- Data Quality implementado.
- IAM Identity Center e Roles configurados.
- CloudWatch Logs validado.
- CI executada com sucesso no GitHub Actions.
- CD manual executado com sucesso utilizando OIDC.

## 2. Recursos AWS principais

**Região:** `us-east-1`

**Bucket:** `rafael-portfolio-tesouro-aws`

**Lambda:** `tesouro-ingestion`

**Glue Job:** `tesouro-bronze-silver-gold`

**Scheduler:** `tesouro-daily-ingestion` — DESATIVADO.

**Repositório:** https://github.com/rafaelbortolottidev-wq/pipeline-tesouro-aws

## 3. Limitação conhecida

O download automatizado do CSV oficial retorna HTTP 429.

A Lambda foi implementada e publicada, mas sua execução ponta a ponta com o Glue não foi validada.

O processamento Bronze → Silver → Gold foi validado com dados já disponíveis no S3.

**A ingestão automática não deve ser apresentada como operacional.**

## 4. Decisões finais

- Não adicionar novos serviços AWS.
- Não realizar novos testes da API nesta versão.
- Manter o Scheduler desativado.
- Preservar o código desenvolvido e as evidências de execução.
- Encerrar a v1.0 com a limitação explicitamente documentada.

## 5. Próxima ação

Gerar o handoff final de encerramento e atualizar o status na Central do Portfólio.

**Não há novas atividades de desenvolvimento previstas para a v1.0.**