<img width="1672" height="941" alt="image" src="https://github.com/user-attachments/assets/8d009cfb-22d8-4f6e-a5fc-eabaaf979139" />

# Pipeline Tesouro Direto AWS 🚀

**Projeto de portfólio | Engenharia de Dados | Python | AWS**

## Objetivo

Desenvolver um pipeline de Engenharia de Dados para ingestão, tratamento, validação e análise de preços e taxas dos títulos do Tesouro Direto.

## Arquitetura

**API CKAN → AWS Lambda → S3 Bronze → AWS Glue → S3 Silver/Gold → Glue Data Catalog → Amazon Athena**

Tecnologias complementares: EventBridge Scheduler, CloudWatch, IAM Identity Center, GitHub Actions e OIDC.

## Resultados comprovados

- **Silver:** 177.260 registros tratados em Parquet.
- **Gold:** 150 registros analíticos.
- Processamento Bronze → Silver → Gold executado com sucesso no AWS Glue.
- Dados catalogados e consultados no Amazon Athena.
- Validações de qualidade implementadas.
- CI com verificações automáticas de Python e testes.
- CD validado com publicação de código na AWS via OIDC.
- IAM Roles específicas para os serviços.

## Limitação conhecida

A fonte oficial CKAN retorna HTTP 429 durante o download automatizado do CSV.

A Lambda foi implementada, mas a ingestão automática e sua integração ponta a ponta com o Glue não puderam ser validadas.

O EventBridge Scheduler permanece desativado. O processamento AWS foi validado utilizando dados previamente armazenados no S3.

## Status

**v1.0 — Encerrada com limitação externa documentada.**

O projeto demonstra implementação prática de ETL serverless, organização de Data Lake, segurança AWS, consultas analíticas e CI/CD.
