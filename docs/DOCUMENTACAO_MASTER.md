---

## Encerramento técnico — v1.0

**Data:** 24/10/2026  
**Status:** Encerrado com limitação externa documentada.

### 1. Entregas validadas

- **Amazon S3:** armazenamento das camadas Bronze, Silver e Gold.
- **AWS Glue Python Shell:** transformação Bronze → Silver → Gold executada com sucesso.
- **Silver:** 177.260 registros em Parquet.
- **Gold:** 150 registros em Parquet.
- **AWS Glue Data Catalog:** catalogação da Gold.
- **Amazon Athena:** consulta SQL validada, confirmando 150 registros.
- **CloudWatch:** logs de execução do processamento.
- **GitHub Actions — CI:** verificações de código e testes automatizados.
- **GitHub Actions — CD:** implantação de código da Lambda e do Glue com autenticação OIDC, executada com sucesso.

### 2. Mapeamento IAM

| Identidade / Role | Responsabilidade |
|---|---|
| `portfolio-admin` | Administração da conta pelo IAM Identity Center, com MFA |
| `TesouroDevAccess` | Permission Set para operações do projeto |
| `tesouro-ingestion-execution-role` | Permitir à Lambda acessar recursos necessários à ingestão, registrar logs e iniciar o Glue |
| `tesouro-etl-execution-role` | Permitir ao Glue ler a Bronze, processar os dados e gravar Silver/Gold |
| `AWSGlueServiceRole-TesouroGoldCrawler` | Permitir ao Crawler catalogar os dados da Gold |
| `tesouro-scheduler-execution-role` | Permitir ao EventBridge Scheduler invocar a Lambda |
| `tesouro-github-actions-role` | Permitir ao GitHub Actions publicar os códigos da Lambda e do Glue via OIDC |

**Observação:** esta tabela descreve as responsabilidades das identidades. As permissões IAM exatas devem ser consultadas nas respectivas políticas AWS.

### 3. Automação e limitação conhecida

A função `tesouro-ingestion` foi desenvolvida e publicada na AWS, incluindo descoberta da fonte CKAN, controle de versões com SHA-256 e integração prevista com o AWS Glue.

Entretanto, a fonte oficial retornou **HTTP 429 — Too Many Requests** durante as tentativas de download automatizado.

Consequentemente:

- A execução integral Lambda → Bronze → Glue não foi validada.
- O EventBridge Scheduler `tesouro-daily-ingestion`, configurado para 21h (America/Sao_Paulo), permanece **desativado**.
- Não houve necessidade de alterar o ETL validado nem incluir novos serviços.

### 4. Decisão de encerramento

A v1.0 foi encerrada como projeto de portfólio, demonstrando processamento de dados na AWS, qualidade, catalogação, segurança e CI/CD.

A ingestão automática permanece como limitação conhecida, não como funcionalidade operacional comprovada.

**Não são necessárias novas implementações ou execuções AWS para este encerramento.**