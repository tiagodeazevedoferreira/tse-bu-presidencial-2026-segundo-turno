# Contexto de continuidade — projeto TSE 2026

Última atualização: 28/10/2026.

## Repositórios e separação de escopo

- Primeiro turno: https://github.com/tiagodeazevedoferreira/tse-bu-presidencial-2026 — preservar sem alterações por este projeto.
- Segundo turno e dashboard atual: https://github.com/tiagodeazevedoferreira/tse-bu-presidencial-2026-segundo-turno
- Branch de trabalho da auditoria/radar: `feat/auditoria-base-radar-anomalias`.
- PR de rascunho nº 2: https://github.com/tiagodeazevedoferreira/tse-bu-presidencial-2026-segundo-turno/pull/2
- Não mesclar o PR nem alterar a publicação principal até concluir a revisão das mudanças.

Este repositório contém duas frentes que devem ser acompanhadas separadamente:
1. pipeline de ingestão e validação de Boletins de Urna oficiais do segundo turno;
2. dashboard descritivo que compara os votos de Lula e Flávio Bolsonaro entre o primeiro e o segundo turnos e prepara um Radar de Anomalias.
Não confundir os dados/artefatos de uma frente com os da outra.

## Decisões metodológicas permanentes

- Usar dados observados, análises descritivas e comparações com cobertura explicitada.
- Não implementar regressão de Goodman, método de King/EI nem outros modelos de inferência ecológica.
- Não inferir trajetórias individuais de eleitores a partir de resultados agregados.
- Um alerta estatístico é uma hipótese para conferência, não prova de fraude nem demonstração de impossibilidade.
- Separar claramente: inconsistência objetiva da base, anomalia estatística e caso que merece investigação.
- Não inventar linhas, votos, seções ou URLs oficiais; ausência de dado não equivale a zero.
- Não alterar o repositório do primeiro turno.
- Não commitar ZIPs brutos nem grandes dados derivados sem necessidade.

## Frente A — pipeline oficial de Boletins de Urna do segundo turno

### Estado conhecido em 26/10/2026

- O repositório do segundo turno existe e tem branch padrão `main`.
- `scripts/inspect_tse_bu_resources.py` consulta a API CKAN oficial e lista metadados, sem baixar ou processar os dados.
- A fonte oficial de BU do segundo turno e seu hash ainda não estavam confirmados na última inspeção documentada.
- A listagem consultada em 26/10/2026 mostrava recursos rotulados como “Primeiro turno”, embora a página do conjunto diga que cobre os dois turnos.
- Não declarar que existe pipeline nacional de BU do segundo turno concluído ou validado sem confirmar a fonte e processar as 27 UFs.

Fontes para conferir:
- https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna
- https://dadosabertos.tse.jus.br/dataset/?tags=Ano+2026

### Estratégia quando a fonte oficial for confirmada

1. Registrar URL de origem, data/hora, hash e esquema.
2. Baixar por UF, validar arquivos e hashes publicados pelo TSE.
3. Inspecionar uma UF piloto antes de adaptar códigos ou campos.
4. Processar em chunks e usar SQLite temporário para limitar consumo de memória.
5. Gerar resultados por UF e consolidação nacional por seção.
6. Validar cobertura das 27 UFs, chaves, valores negativos, totais, comparecimento, eleitorado e consistência entre arquivos.
7. Só declarar conclusão nacional após os controles de integridade passarem.

## Frente B — dashboard de crescimento entre turnos e Radar de Anomalias

### Objetivo funcional

O dashboard “Presidencial 2026: crescimento entre turnos” compara os votos de Lula e Flávio Bolsonaro no primeiro e no segundo turnos. Os filtros permitem partir do panorama nacional e descer por região, UF, município, local de votação, zona e seção eleitoral. A fonte declarada para esse dashboard é o CSV do TSE em `data/NovoArquivoDashboard.csv`.

O objetivo analítico é identificar padrões inesperados e casos extremos para investigação, inclusive em recortes geográficos detalhados. Os alertas devem explicar a regra que os gerou e preservar os valores de origem; não devem classificar automaticamente um resultado como fraude.

### Limitações da fonte atual

- O CSV contém chaves geográficas e votos de Lula e Flávio nos dois turnos.
- A base não contém todos os campos necessários para validar comparecimento, abstenção, votos brancos/nulos e eleitorado.
- Uma variação de votos entre turnos, por si só, não demonstra erro ou irregularidade.
- Não interpretar a participação calculada somente com Lula e Flávio como participação oficial sobre todos os votos válidos.
- Quando o voto inicial for zero, a variação percentual deve ser “não calculável”, e não infinito ou zero.
- Ausências, valores inválidos e zero são estados diferentes e devem permanecer distintos.

### Auditoria da base — resultado local em 28/10/2026

Script: `tools/audit_dashboard_csv.py`.
Relatório local: `reports/auditoria_csv_dashboard.json`.
Plano: `docs/PLANO-RADAR-ANOMALIAS.md`.
Testes: `tests/test_audit_dashboard_csv.py`.
Workflow: `.github/workflows/test-auditoria-csv.yml`.

O script lê o CSV em streaming, detecta o delimitador, valida o esquema e os campos numéricos e verifica chaves geográficas duplicadas usando SQLite temporário. Não modifica a fonte por conta própria.

Após corrigir alterações manuais introduzidas no Excel, a execução local da auditoria retornou:
- 499.205 linhas de dados;
- 0 linhas vazias;
- 0 linhas com quantidade incorreta de colunas;
- 0 chaves geográficas incompletas;
- 499.205 chaves de seção únicas e 0 duplicidades;
- 0 votos negativos;
- 0 valores numéricos inválidos;
- 0 linhas com votos parciais em qualquer turno.

O usuário informou que os valores `0,01` nas colunas do Flávio eram alterações manuais feitas no Excel para facilitar a inspeção e que o valor original desses casos era zero. Foram restauradas 80 ocorrências na coluna do primeiro turno e 50 na do segundo turno. Foi criado localmente o backup `data/NovoArquivoDashboard.csv.backup`; não adicionar esse backup ao Git.

Tamanho observado do CSV local corrigido: 37.561.673 bytes. O tamanho/diff do arquivo em relação à versão rastreada pelo Git ainda precisa ser revisado antes de decidir se a fonte corrigida deve ser incluída no PR. A auditoria verifica consistência estrutural interna; não compara automaticamente todos os votos com uma fonte independente do TSE.

### Testes e GitHub Actions

- Execução local: `py -m unittest discover -s tests -v` — 4 testes passaram.
- GitHub Actions “Teste da auditoria do CSV”: execução nº 4 concluída com sucesso para o commit `3f831002efcfe0caf837d357bf416f982c1f13ea`.
- PR nº 2 permanece aberto como rascunho, sem merge.
- Os quatro arquivos de implementação da auditoria já estão rastreados na branch: `tools/audit_dashboard_csv.py`, `docs/PLANO-RADAR-ANOMALIAS.md`, `tests/test_audit_dashboard_csv.py` e `.github/workflows/test-auditoria-csv.yml`.

### Plano técnico do Radar

1. **Integridade e cobertura:** verificar esquema, codificação, cobertura de turnos e correspondência de seções.
2. **Métricas descritivas:** variação absoluta, variação percentual quando calculável, participação relativa claramente definida, mudança em pontos percentuais e alteração da margem entre candidatos.
3. **Detecção estatística:** começar por regras transparentes e casos extremos; comparar unidades com grupos de referência comparáveis; avaliar mediana e desvio absoluto mediano (MAD), tratando MAD igual a zero; documentar limiares e múltiplos testes.
4. **Interface investigativa:** ranking de alertas com filtros geográficos, dispersão entre mudanças dos candidatos, detalhes até seção com valores de origem e motivo do alerta, e exportação dos casos filtrados.
5. **Rotulagem:** diferenciar inconsistência objetiva, anomalia estatística e caso para investigação.

Manter o CSV como fonte de referência até concluir a auditoria. Só então medir alternativas derivadas (por exemplo, JSON gzip ou arrays compactos), comparando tamanho transferido, tempo de renderização e memória. Não adotar Parquet/DuckDB-WASM sem evidência de que uma solução mais simples não atende.

## Estado operacional local e próxima ação

No último estado informado pelo usuário:
- Branch local: `feat/auditoria-base-radar-anomalias`.
- `git diff --check` terminou sem saída, sem apontar problemas de whitespace.
- `git status --short` mostrou `data/NovoArquivoDashboard.csv` modificado, `reports/auditoria_csv_dashboard.json` e outros artefatos de investigação não rastreados.
- Há scripts e arquivos CSV/PDF/ZIP de investigação em `reports/` e na raiz/`data/`; não adicioná-los em lote. Não incluir o backup.
- A tentativa de visualizar o diff foi digitada como `mgit diff ...`, portanto o comando não foi executado. O próximo comando correto é:

```powershell
git diff -- data/NovoArquivoDashboard.csv | Select-Object -First 120
```

Inspecionar esse diff antes de decidir se o CSV deve entrar no PR. Em seguida, selecionar explicitamente os arquivos da auditoria para staging, revisar `git diff --cached`, e só então preparar commit/push. Não fazer merge nem alterar `main` sem revisão.

## Regras para avançar

- Não declarar que o dashboard ou o CSV foram validados contra todos os dados oficiais apenas com base na auditoria estrutural.
- Não afirmar que o arquivo corrigido foi commitado ou enviado: a correção está apenas no ambiente local neste estado.
- Não afirmar que o diff do CSV contém somente as correções esperadas até inspecioná-lo.
- Manter documentadas as decisões, os resultados reproduzíveis, as limitações e a próxima tarefa para permitir continuidade em outro chat.
