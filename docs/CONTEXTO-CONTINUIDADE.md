# Contexto de continuidade — projeto TSE 2026

Última atualização: 30/10/2026.

## Atualização de continuidade — 05/11/2026

### Estado Git informado localmente

- Branch ativa: `feat/auditoria-base-radar-anomalias`.
- HEAD local e `origin/feat/auditoria-base-radar-anomalias`: `8374b77` (`docs: atualiza contexto da auditoria nacional de BU`).
- `git log --oneline origin/main..HEAD`: 17 commits na branch além de `origin/main`.
- `git diff --stat origin/main...HEAD`: 36 arquivos, 2.690 inserções e 41 exclusões, incluindo auditoria nacional de BU, relatórios por UF, testes e documentação.
- `git status --short` mostrou somente arquivos não rastreados; nenhum arquivo rastreado modificado foi listado. Isso não equivale a working tree totalmente limpo.
- Arquivos não rastreados observados: `coletar_amostra.py`, `coletar_piloto_100.py`, `data/NovoArquivoDashboard.csv.backup`, `data/favio-diminuiu.csv`, `data/secoes_flavio_ate_100_votos_segundo_turno - Copia.csv`, `exportar_secao.py`, `identificar_candidatos.py`, `inspecionar_bu.py`, `reports/investigacao/`, `reports/tse_arquivos_totalizacao.json`, `reports/tse_bu_resources.json`, `reports/tse_bu_resources_20261029.json`, `reports/tse_resultados_2026_resources.json`, `secoes_flavio_ate_100_votos_segundo_turno.csv`, `secoes_flavio_zero_somente_segundo_turno.csv` e `testar_bu.py`.
- Não executar `git add .`, `git clean` ou descarte em lote. Não adicionar automaticamente esses artefatos ao PR. O backup não deve ser commitado.

### CSV principal e backup — verificação em 05/11/2026

Hashes SHA-256 informados pelo usuário:

- `data/NovoArquivoDashboard.csv`: `D7B001DFFAEDCD9C059F3DC5E9A3937654D2A64296CA1E8BFD57488C21832A27`.
- `data/NovoArquivoDashboard.csv.backup`: `060B925392B5D3D0A623F6BADD0C232094E2B2D5DB68F2860092D8035A91DC84`.

Os hashes diferentes comprovam que os arquivos não são idênticos byte a byte; isoladamente, não demonstram que a única diferença sejam as 130 células esperadas. Há registro anterior de 499.205 linhas em cada arquivo e da restauração de 80 ocorrências de `0,01` para `0` no primeiro turno e 50 no segundo turno. Esse total de 130 alterações deve ser revalidado por comparação direta entre os arquivos antes de ser tratado como resultado confirmado da comparação atual.

### Próxima tarefa — auditoria comparativa não destrutiva

1. Preservar o CSV atual e o backup; não sobrescrever nenhum deles.
2. Comparar os arquivos por chave geográfica e por coluna, contando linhas/células alteradas e registrando valores anterior/atual.
3. Confirmar se as diferenças se limitam às 130 restaurações esperadas (80 no primeiro turno e 50 no segundo), ou identificar diferenças adicionais.
4. Verificar cabeçalho, delimitador, codificação, número de registros e chaves; não confiar apenas em hashes ou contagem de linhas.
5. Gerar relatório separado em `reports/investigacao/` sem modificar a fonte.
6. Só depois decidir se a versão corrigida do CSV deve ser incluída no PR nº 2. Não incluir o backup, scripts exploratórios ou CSVs derivados sem revisão individual.
7. Manter o PR nº 2 em rascunho; não fazer merge nem alterar `main` sem autorização explícita.

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

### Estado da fonte e processamento nacional — 30/10/2026

- O script `tools/audit_dashboard_national_bu.py` descobre os recursos oficiais pela API CKAN do conjunto `resultados-2026-boletim-de-urna`, baixa/usa os ZIPs por UF, verifica os sidecars SHA-512, mantém cache temporário e executa a auditoria por UF, produzindo relatórios estaduais e consolidação nacional.
- Foi corrigida a descoberta de recursos quando o CKAN informa uma URL terminada em `.zip.sha512`: o script reconhece o sidecar e recupera a URL do ZIP correspondente.
- A correção está coberta por teste de regressão: `test_discovers_zip_when_ckan_resource_url_points_to_sha512_sidecar`.
- Commits da correção e do teste:
  - `9c135c5 fix: reconhece recursos CKAN publicados como sidecar SHA-512`
  - `8018fe4 test: cobre URL CKAN de ZIP publicada como SHA-512`
- Testes direcionados: `py -m unittest tests.test_audit_dashboard_national_bu -v` — 5 testes passaram.
- Validação isolada de RR: 1.519 chaves do dashboard, 1.519 chaves de BU e 1.519 chaves em comum; zero divergências de Lula e Flávio; zero falhas técnicas.
- Auditoria nacional executada com sucesso para as 27 UFs:
  - `status`: `concluido_sem_divergencias_em_todas_as_ufs`;
  - UFs solicitadas: 27; UFs com resultado: 27;
  - UFs concluídas sem divergências: 27;
  - UFs com divergências ou revisão: 0;
  - falhas técnicas ou recursos ausentes: 0;
  - em todas as UFs, divergências de votos de Lula: 0; divergências de votos de Flávio Bolsonaro: 0.
- Em RR, a auditoria nacional confirmou novamente 1.519 chaves correspondentes, sem divergências.
- Relatório consolidado: `reports/auditoria_nacional_bu.json`.
- Relatórios por UF: `reports/auditoria_nacional_bu/auditoria_bu_dashboard_<UF>.json`, total de 27 arquivos.
- Os 28 relatórios foram versionados no commit `7f8c639 docs: registra auditoria nacional dos boletins de urna` (1.448 linhas adicionadas) e enviados com sucesso para `origin/feat/auditoria-base-radar-anomalias`. O push confirmou a atualização remota de `8018fe4` para `7f8c639`.

**Escopo e interpretação do resultado:** a auditoria compara, seção por seção, os votos nominais de Lula (13) e Flávio Bolsonaro (22) no segundo turno, usando o CSV do dashboard e os dados oficiais de Boletins de Urna. O resultado sem divergências cobre esses dois candidatos e esse turno; não valida todos os candidatos, todos os aspectos do processo eleitoral ou a correção de toda a base do primeiro turno. Também não prova nem descarta fraude eleitoral.

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

### Auditoria estrutural do CSV — resultado local em 28/10/2026

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

Tamanho observado do CSV local corrigido: 37.561.673 bytes. A correção do CSV permanece sujeita à revisão do diff antes de decidir se a fonte deve entrar no PR. A auditoria nacional de BU do segundo turno descrita na Frente A não substitui essa revisão nem valida o primeiro turno.

### Testes e GitHub Actions

- Execução local mais recente registrada: `py -m unittest discover -s tests -v` — 6 testes passaram, incluindo os testes de auditoria de BU.
- GitHub Actions “Teste da auditoria do CSV”: execução nº 4 concluída com sucesso para o commit `3f831002efcfe0caf837d357bf416f982c1f13ea`.
- PR nº 2 permanece aberto como rascunho, sem merge.
- Os arquivos de implementação da auditoria estrutural já rastreados na branch: `tools/audit_dashboard_csv.py`, `docs/PLANO-RADAR-ANOMALIAS.md`, `tests/test_audit_dashboard_csv.py` e `.github/workflows/test-auditoria-csv.yml`.

### Plano técnico do Radar

1. **Integridade e cobertura:** verificar esquema, codificação, cobertura de turnos e correspondência de seções.
2. **Métricas descritivas:** variação absoluta, variação percentual quando calculável, participação relativa claramente definida, mudança em pontos percentuais e alteração da margem entre candidatos.
3. **Detecção estatística:** começar por regras transparentes e casos extremos; comparar unidades com grupos de referência comparáveis; avaliar mediana e desvio absoluto mediano (MAD), tratando MAD igual a zero; documentar limiares e múltiplos testes.
4. **Interface investigativa:** ranking de alertas com filtros geográficos, dispersão entre mudanças dos candidatos, detalhes até seção com valores de origem e motivo do alerta, e exportação dos casos filtrados.
5. **Rotulagem:** diferenciar inconsistência objetiva, anomalia estatística e caso para investigação.

Manter o CSV como fonte de referência até concluir a auditoria. Só então medir alternativas derivadas (por exemplo, JSON gzip ou arrays compactos), comparando tamanho transferido, tempo de renderização e memória. Não adotar Parquet/DuckDB-WASM sem evidência de que uma solução mais simples não atende.

## Estado operacional e próxima ação

Estado confirmado em 30/10/2026:
- Branch de trabalho: `feat/auditoria-base-radar-anomalias`.
- Último commit local informado: `7f8c639`, com os 28 relatórios da auditoria nacional.
- Push para `origin/feat/auditoria-base-radar-anomalias` concluído com sucesso; o remoto avançou de `8018fe4` para `7f8c639`.
- PR nº 2 continua em rascunho e não foi mesclado.
- Há arquivos auxiliares e resultados locais não rastreados de investigações anteriores. Não adicioná-los em lote.
- O backup `data/NovoArquivoDashboard.csv.backup` não deve ser commitado.
- O estado atual do working tree após o commit/push ainda precisa ser verificado com `git status --short`.

### Próxima sequência recomendada

1. Atualizar este documento de continuidade e versionar a atualização na mesma branch.
2. Verificar o estado local com `git status --short` e `git log -3 --oneline`.
3. Inspecionar o diff do CSV corrigido antes de decidir se ele deve entrar no PR:
   ```powershell
   git diff -- data/NovoArquivoDashboard.csv | Select-Object -First 120
   ```
4. Não incluir scripts auxiliares, CSVs de investigação, relatórios exploratórios ou o backup sem uma decisão explícita sobre cada artefato.
5. Depois de revisar os arquivos e testes, atualizar o PR nº 2. Não fazer merge nem alterar `main` sem autorização explícita.

## Regras para avançar

- Não declarar que o dashboard ou o CSV foram validados contra todos os dados oficiais apenas com base na auditoria estrutural.
- Não confundir a auditoria nacional de BU do segundo turno (Lula e Flávio, por seção) com uma validação integral do CSV, do primeiro turno ou de todos os candidatos.
- Não afirmar que o arquivo corrigido foi commitado ou enviado: a correção do CSV continua pendente de inspeção do diff e decisão de versionamento.
- Não afirmar que o working tree está limpo sem verificar `git status --short`.
- Manter documentadas as decisões, os resultados reproduzíveis, as limitações e a próxima tarefa para permitir continuidade em outro chat.
