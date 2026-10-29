# Executar a auditoria nacional dos BUs

## Escopo

A rotina compara o CSV `data/NovoArquivoDashboard.csv` com os Boletins de Urna oficiais do **segundo turno**, seção por seção, para os votos nominais de Lula (código 13) e Flávio Bolsonaro (código 22). A rotina valida o SHA-512 publicado, testa a integridade dos ZIPs e gera um relatório por UF mais um resumo nacional.

Esta auditoria não examina o primeiro turno, outros candidatos nem todos os campos eleitorais do BU. Divergências exigem revisão; não são, isoladamente, prova de fraude.

## Requisitos

- Python 3.10 ou superior.
- Acesso à internet para consultar a API do TSE e baixar arquivos.
- Executar os comandos a partir da raiz do repositório.

## Atualizar a cópia local

No PowerShell:

```powershell
git switch feat/auditoria-base-radar-anomalias
git pull origin feat/auditoria-base-radar-anomalias
```

## Execução nacional

```powershell
py .\tools\audit_dashboard_national_bu.py
```

Por padrão, a rotina processa as 27 UFs com até quatro tarefas concorrentes. Para reduzir ou aumentar a concorrência (limite máximo 8):

```powershell
py .\tools\audit_dashboard_national_bu.py --workers 2
```

Para testar primeiro duas UFs:

```powershell
py .\tools\audit_dashboard_national_bu.py --ufs RR AC
```

## Saídas e retomada

- Relatórios individuais: `reports/auditoria_nacional_bu/auditoria_bu_dashboard_<UF>.json`.
- Resumo nacional: `reports/auditoria_nacional_bu.json`.
- Cache de ZIPs e hashes válidos: pasta `tse_bu_nacional_2026` dentro da pasta temporária do Windows.

Na execução seguinte, os ZIPs em cache só são reutilizados quando seu SHA-512 corresponde ao hash publicado pelo TSE. Se um arquivo estiver ausente ou não corresponder ao hash, será baixado novamente. Uma falha em uma UF não impede a tentativa das demais; o resumo sinaliza falhas técnicas, recursos ausentes e revisões necessárias.

O status nacional só será `concluido_sem_divergencias_em_todas_as_ufs` quando todas as UFs solicitadas tiverem sido processadas sem divergências. Uma execução parcial ou com falhas não deve ser descrita como auditoria nacional concluída.

## Testes automatizados

```powershell
py -m unittest discover -s tests -v
```
