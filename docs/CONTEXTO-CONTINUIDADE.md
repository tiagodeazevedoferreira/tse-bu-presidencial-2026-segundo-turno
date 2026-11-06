# Contexto de continuidade — projeto TSE 2026

Última atualização: 06/11/2026.

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


## Atualização de continuidade — 06/11/2026: comparação forense do CSV concluída

### Resultado confirmado localmente

Foi executada uma comparação não destrutiva entre `data/NovoArquivoDashboard.csv` (atual) e `data/NovoArquivoDashboard.csv.backup`, usando chave geográfica composta por UF, município, zona e seção. A comparação abrangeu as 10 colunas e produziu o relatório local `reports/investigacao/comparacao_csv.json`.

Resultados apresentados no console:

- Linhas no backup: 499.205.
- Linhas no CSV atual: 499.205.
- Cabeçalhos: 10, idênticos.
- Delimitador: ponto e vírgula (`;`).
- Chaves duplicadas no backup: 0.
- Chaves duplicadas no atual: 0.
- Linhas inválidas no backup/atual: 0.
- Chaves somente no atual: 0.
- Chaves somente no backup: 0.
- Linhas com alterações: 80.
- Células alteradas: 130.
- Alterações por coluna: 80 na coluna de Flávio no 1º turno e 50 na coluna de Flávio no 2º turno.
- Nenhuma alteração foi registrada nas demais colunas, incluindo as colunas de Lula, identificadores e localização.
- Status produzido pelo script: `comparacao_concluida`.

Uma segunda leitura do relatório confirmou os valores exatos de todas as 130 células:

- Flávio – 1º turno: 80 ocorrências de `0,01` no backup para `0` no CSV atual.
- Flávio – 2º turno: 50 ocorrências de `0,01` no backup para `0` no CSV atual.
- Total: 130 alterações, sem outras combinações de valores.

### Conclusão e limites

A comparação direta confirma que, no escopo das colunas e chaves comparadas, o CSV atual preserva os 499.205 registros e apresenta exatamente as 130 correções esperadas. Não foram encontradas diferenças adicionais, chaves ausentes, duplicidades ou linhas inválidas.

Esta conclusão é uma comparação entre o CSV atual e o backup local; não substitui a validação contra a fonte oficial do TSE nem amplia o escopo da auditoria nacional de BU já documentada. Os cabeçalhos foram considerados idênticos pelos bytes/texto lidos pelo script, embora a exibição no console tenha mostrado caracteres acentuados como `?`; a questão de codificação/legibilidade dos nomes de colunas não foi investigada nesta etapa.

O relatório `reports/investigacao/comparacao_csv.json` foi gerado localmente e não foi commitado. O backup permanece local e não deve ser versionado. Não foi feita alteração no CSV durante a comparação. A inclusão do CSV corrigido no PR continua condicionada à inspeção do diff e à decisão explícita de versionamento.

### Próximas ações

1. Verificar o estado local com `git status --short` e `git log -3 --oneline`, pois a lista anterior de arquivos não rastreados ainda precisa ser atualizada.
2. Inspecionar o diff de `data/NovoArquivoDashboard.csv` antes de decidir se o arquivo corrigido entra no PR.
3. Revisar individualmente os artefatos locais; não executar `git add .`, `git clean` nem adicionar o backup.
4. Manter o PR nº 2 em rascunho; não fazer merge nem alterar `main` sem autorização explícita.

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


## Atualização de continuidade — 06/11/2026: inventário dos artefatos locais e revisão do commit bcf41a7

### Verificações Git informadas pelo usuário

Comandos executados na branch local feat/auditoria-base-radar-anomalias:

    git show --stat --oneline bcf41a7
    git status --short

Saída do commit:

- bcf41a7 Corrige zeros no CSV e atualiza relatório de auditoria
- data/NovoArquivoDashboard.csv: 160 linhas alteradas no diff do commit.
- reports/auditoria_csv_dashboard.json: 100 linhas adicionadas.
- Total: 2 arquivos alterados, 180 inserções e 80 exclusões.

Conclusão: o commit bcf41a7 registra conjuntamente a atualização do CSV e o relatório da auditoria estrutural. A verificação local anterior também informou que o CSV está rastreado pelo Git e que seu diff atual contra origin/main é vazio. Portanto, não criar outro commit para reapresentar o CSV sem antes verificar o estado atual da branch e do PR.

A saída de git status --short contém somente entradas ??, ou seja, os seguintes itens estavam não rastreados no momento da execução:

- Scripts: coletar_amostra.py, coletar_piloto_100.py, exportar_secao.py, identificar_candidatos.py, inspecionar_bu.py, testar_bu.py.
- Arquivos de dados: data/NovoArquivoDashboard.csv.backup, data/favio-diminuiu.csv, data/secoes_flavio_ate_100_votos_segundo_turno - Copia.csv, secoes_flavio_ate_100_votos_segundo_turno.csv, secoes_flavio_zero_somente_segundo_turno.csv.
- Diretório: reports/investigacao/.
- Metadados TSE: reports/tse_arquivos_totalizacao.json, reports/tse_bu_resources.json, reports/tse_bu_resources_20261029.json, reports/tse_resultados_2026_resources.json.

A lista é um retrato do git status informado pelo usuário, não uma confirmação de que o estado local continua igual neste momento. Não executar git add ., git clean, exclusões ou commits em lote.

### Inventário de reports/investigacao/

O usuário listou os seguintes arquivos locais:

| Arquivo | Tamanho informado | Observação |
|---|---:|---|
| comparacao_csv.json | 32.433 bytes | Relatório da comparação forense entre CSV atual e backup, descrita acima |
| leiame.pdf | 192.420 bytes | Documento de orientação associado ao conjunto de dados; conteúdo ainda não inspecionado |
| votacao_secao_2026_BR.csv | aproximadamente 510.851.000 bytes (saída truncou a unidade/valor final) | CSV de votação por seção; conteúdo, origem e esquema ainda precisam ser inspecionados |
| votacao_secao_2026_BR.zip | 161.616.519 bytes | Arquivo compactado de grande porte; não versionar sem necessidade explícita |

O tamanho do CSV foi truncado pela formatação da tabela PowerShell; não registrar um tamanho exato até executar uma listagem que exponha o valor completo em bytes. O ZIP e o CSV devem ser considerados artefatos brutos/derivados de investigação até confirmação de sua origem, cobertura, esquema e necessidade. Não adicioná-los ao Git nem apagá-los nesta etapa.

### Inspeção preliminar dos scripts exploratórios

Os primeiros 50 registros de cada script foram apresentados pelo usuário:

- coletar_amostra.py: usa asn1tools, HTTP e JSON para acessar arquivos de BU do TSE. As constantes apontam para o caminho ele2026/arquivo-urna/3221, configuração de SP e diretório local dados_bu. É um coletor exploratório de BUs, mas o restante do código ainda precisa ser lido antes de avaliar integridade, escopo e reprodutibilidade.
- coletar_piloto_100.py: implementa coleta piloto com checkpoint, diretório de arquivos brutos, CSV de resultados e relatório de status. A constante LIMITE está definida como 200, apesar do nome do arquivo/script mencionar 100; verificar a semântica e o restante do código antes de reutilizar.
- exportar_secao.py: decodifica um BU local (bu-teste.dat) com o esquema bu_2026.asn1, extrai resultados por cargo e votos nominais/brancos/nulos e prepara linhas para exportação. O mapeamento de candidatos exibido é ilustrativo/genérico (códigos 13 e 22), devendo ser confrontado com os metadados oficiais e o contexto da eleição antes de qualquer uso analítico.
- identificar_candidatos.py: inspeciona os resultados decodificados e imprime códigos/tipos/identificações dos votáveis.
- inspecionar_bu.py: imprime identificação da seção, estrutura de resultados e campos adicionais do BU, como comparecimento e habilitação.
- testar_bu.py: testa compilação do esquema ASN.1 e tenta decodificar o arquivo como envelope e, em fallback, diretamente como BU.

Os quatro últimos scripts são ferramentas de inspeção/validação exploratória que dependem de arquivos locais (bu_2026.asn1 e bu-teste.dat) não incluídos no inventário apresentado. Não assumir que podem ser executados em outro ambiente. Antes de incorporá-los ao projeto, verificar dependências, parâmetros, tratamento de erros, origem dos arquivos, cobertura, testes e relação com o pipeline oficial já versionado.

### Outros relatórios JSON listados em reports/

O usuário informou a existência local dos seguintes arquivos:

- auditoria_bu_dashboard_RR.json — 1.704 bytes.
- auditoria_csv_dashboard.json — 2.543 bytes.
- auditoria_nacional_bu.json — 15.769 bytes.
- tse_arquivos_totalizacao.json — 19.451 bytes.
- tse_bu_resources.json — 28.088 bytes.
- tse_bu_resources_20261029.json — 82.960 bytes.
- tse_resultados_2026_resources.json — 30.499 bytes.

A presença de um arquivo no diretório não demonstra que esteja não rastreado: o status fornecido lista como não rastreados apenas os quatro arquivos tse_*; os relatórios de auditoria citados não aparecem como ?? nessa saída. O relatório auditoria_csv_dashboard.json já aparece no commit bcf41a7. Não duplicar ou recriar relatórios já versionados.

### Classificação preliminar e decisões

1. Manter localmente: data/NovoArquivoDashboard.csv.backup; não versionar backup.
2. Não versionar sem justificativa específica: ZIP bruto de 161.616.519 bytes e CSV extraído de aproximadamente 510,9 MB.
3. Scripts exploratórios: manter preservados localmente; avaliar individualmente se algum deve ser promovido a ferramenta oficial, com parâmetros configuráveis, documentação e testes.
4. Relatórios de descoberta TSE: podem ter valor de rastreabilidade, mas comparar seu conteúdo, data, URL e sobreposição com os relatórios já versionados antes de decidir.
5. Relatório de comparação: reports/investigacao/comparacao_csv.json documenta a comparação local; decidir se deve ser versionado após inspecionar o conteúdo, remover caminhos absolutos/dados desnecessários e confirmar que não duplica outro relatório.
6. PDF e CSV da investigação: inspecionar leiame.pdf e metadados/cabeçalho/amostra do CSV para confirmar origem e finalidade antes de qualquer decisão.
7. Não fazer limpeza: nenhum arquivo deve ser removido com base apenas no nome ou tamanho.

### Próximas ações técnicas

1. Atualizar o estado local com git status --short, git log -5 --oneline e confirmar o HEAD/branch antes de novas alterações.
2. Inspecionar reports/investigacao/leiame.pdf e os metadados do ZIP/CSV (origem, data, tamanho exato, cabeçalho, delimitador, codificação e número de registros) sem carregar o CSV inteiro na memória.
3. Ler o restante dos scripts exploratórios, especialmente coletar_amostra.py e coletar_piloto_100.py, e identificar dependências e arquivos de entrada/saída.
4. Comparar os quatro JSON tse_* com os recursos já documentados e verificar se há dados sensíveis, caminhos locais ou conteúdo redundante.
5. Decidir individualmente o destino dos artefatos; não adicionar grandes arquivos brutos/derivados ao PR nº 2.
6. Manter o PR nº 2 em rascunho e não fazer merge nem alterar main sem autorização explícita.

**Estado de segurança:** nenhuma alteração local foi feita por esta atualização de contexto. A atualização deste documento no GitHub deve ser registrada como commit isolado na branch feat/auditoria-base-radar-anomalias; não alterar o CSV, os arquivos de investigação ou a main.


## Complemento de evidências — 06/11/2026: metadados e amostra do CSV de votação por seção

O usuário executou comandos PowerShell para obter os tamanhos exatos e inspecionar as cinco primeiras linhas de reports/investigacao/votacao_secao_2026_BR.csv, além de imprimir reports/investigacao/comparacao_csv.json.

### Tamanhos exatos informados

- votacao_secao_2026_BR.zip: 161.616.519 bytes.
- votacao_secao_2026_BR.csv: 1.052.510.851 bytes (aproximadamente 1,05 GB decimal / 1,00 GiB).
- leiame.pdf: 192.420 bytes.
- comparacao_csv.json: 32.433 bytes.

Correção do inventário anterior: o tamanho do CSV não é aproximadamente 510,9 MB; o valor exato informado posteriormente é 1.052.510.851 bytes. Não versionar o ZIP ou o CSV bruto no repositório sem justificativa e estratégia específica de armazenamento de dados. O PDF ainda não foi anexado/inspecionado em conteúdo; somente seu tamanho foi informado.

### Cabeçalho observado do CSV

O cabeçalho tem 26 campos, separados por ponto e vírgula e entre aspas: DT_GERACAO, HH_GERACAO, ANO_ELEICAO, CD_TIPO_ELEICAO, NM_TIPO_ELEICAO, NR_TURNO, CD_ELEICAO, DS_ELEICAO, DT_ELEICAO, TP_ABRANGENCIA, SG_UF, SG_UE, NM_UE, CD_MUNICIPIO, NM_MUNICIPIO, NR_ZONA, NR_SECAO, CD_CARGO, DS_CARGO, NR_VOTAVEL, NM_VOTAVEL, QT_VOTOS, NR_LOCAL_VOTACAO, SQ_CANDIDATO, NM_LOCAL_VOTACAO, DS_LOCAL_VOTACAO_ENDERECO.

Campos particularmente relevantes: identificação geográfica (SG_UF, CD_MUNICIPIO, NM_MUNICIPIO, NR_ZONA, NR_SECAO); dimensão eleitoral (ANO_ELEICAO, CD_ELEICAO, NR_TURNO, CD_CARGO, DS_CARGO); votável e quantidade (NR_VOTAVEL, NM_VOTAVEL, QT_VOTOS, SQ_CANDIDATO); local de votação (NR_LOCAL_VOTACAO, NM_LOCAL_VOTACAO, DS_LOCAL_VOTACAO_ENDERECO); proveniência temporal (DT_GERACAO, HH_GERACAO, DT_ELEICAO). O CSV usa delimitador ponto e vírgula. A codificação ainda não foi confirmada formalmente.

### O que a amostra permite afirmar — e o que não permite

As primeiras linhas exibidas apresentam DT_GERACAO=06/10/2026, HH_GERACAO=14:03:43, ANO_ELEICAO=2026, CD_ELEICAO=6257, DS_ELEICAO=Eleição Geral Federal 2026, DT_ELEICAO=04/10/2026, NR_TURNO=1 nas quatro linhas de dados exibidas e CD_CARGO=1 / DS_CARGO=Presidente nas quatro linhas. A amostra contém municípios do RS e registros por zona, seção, local, votável e quantidade de votos.

Está comprovado que a amostra inicial contém dados de votação por seção para o primeiro turno presidencial. Não está comprovado ainda se o arquivo completo contém também o segundo turno, todos os cargos, todas as UFs, todos os tipos de votável ou se é um recorte específico. Não extrapolar a amostra inicial para o conjunto completo.

A base aparenta oferecer granularidade por seção e dimensões de turno, cargo, votável e local de votação. Isso pode permitir cruzamentos com o dashboard, mas qualquer integração depende de confirmar cobertura, semântica, codificação, chaves e compatibilidade temporal. Para junções, preferir códigos oficiais (por exemplo CD_MUNICIPIO, NR_ZONA, NR_SECAO) em vez de nomes textuais; incluir NR_TURNO e CD_CARGO na chave lógica quando aplicável. Não assumir que SQ_CANDIDATO equivale a NR_VOTAVEL: são campos distintos.

### Atualização do relatório comparacao_csv.json

O conteúdo impresso confirma: linhas_backup=499.205 e linhas_atual=499.205; 10 colunas e cabeçalhos idênticos; delimitador ponto e vírgula; zero chaves duplicadas em ambas as bases; zero linhas inválidas em ambas as bases; 80 linhas com alterações e 130 células alteradas; 80 alterações na coluna de Flávio do primeiro turno e 50 na coluna de Flávio do segundo turno; nenhuma chave somente na base atual ou somente no backup. As alterações listadas restauram valores de 0,01 no backup para 0 no CSV atual.

A saída de console apresenta caracteres acentuados corrompidos em algumas chaves e cabeçalhos (por exemplo Fl?vio e PORTO PRÃNCIPE). Isso pode decorrer de decodificação/codificação no PowerShell ou de bytes já corrompidos no JSON. A causa ainda não foi determinada. Não corrigir o relatório nem os CSVs por inferência; verificar primeiro os bytes e reler explicitamente em UTF-8, comparando com a codificação real do arquivo.

### Próximas verificações obrigatórias do CSV de 1,05 GB

1. Confirmar codificação e BOM, delimitador e consistência de 26 colunas.
2. Contar registros por NR_TURNO e CD_CARGO.
3. Identificar valores distintos de SG_UF, CD_ELEICAO, DT_ELEICAO e DS_ELEICAO.
4. Confirmar se há NR_TURNO=2 e quais candidatos/opções aparecem nesse turno para CD_CARGO=1.
5. Contar linhas e chaves distintas por turno/cargo, verificando duplicidade na granularidade esperada.
6. Comparar cobertura geográfica e chaves com o dashboard, sem presumir equivalência entre as fontes.
7. Inspecionar leiame.pdf para confirmar nome oficial do arquivo, origem, data de extração, leiaute e escopo.

Executar perfilamento em streaming, sem carregar o CSV inteiro na memória. Não executar ainda junção completa, substituição de fonte do dashboard ou cálculo de anomalias a partir dessa base. Primeiro estabelecer perfil e proveniência.

Este complemento registra apenas os resultados fornecidos pelo usuário. Não houve inspeção direta dos bytes do CSV/ZIP/PDF, nem alteração dos arquivos locais. Manter a branch de trabalho e o PR nº 2 sem merge; não modificar main.


## Atualização da investigação — codificação do CSV nacional de votação por seção

Diagnóstico executado localmente em 06/11/2026 para `reports/investigacao/votacao_secao_2026_BR.csv`:

- O arquivo não pode ser decodificado como UTF-8: o teste falhou com `UnicodeDecodeError` no byte de posição 395 (byte `0xE7`).
- A amostra de 1.000 bytes foi decodificada com sucesso usando `cp1252` e `latin-1`. O texto resultante exibiu corretamente caracteres acentuados em nomes e descrições, por exemplo `Eleição Ordinária` e `Eleição Geral Federal 2026`.
- O resultado é compatível com arquivo em Windows-1252, mas o teste cobriu somente a amostra lida; ainda não foi feita validação integral da codificação do arquivo. `latin-1` decodifica qualquer sequência de bytes, portanto seu sucesso isolado não identifica a codificação.
- O cabeçalho confirmado contém 26 colunas, separadas por ponto e vírgula: `DT_GERACAO`, `HH_GERACAO`, `ANO_ELEICAO`, `CD_TIPO_ELEICAO`, `NM_TIPO_ELEICAO`, `NR_TURNO`, `CD_ELEICAO`, `DS_ELEICAO`, `DT_ELEICAO`, `TP_ABRANGENCIA`, `SG_UF`, `SG_UE`, `NM_UE`, `CD_MUNICIPIO`, `NM_MUNICIPIO`, `NR_ZONA`, `NR_SECAO`, `CD_CARGO`, `DS_CARGO`, `NR_VOTAVEL`, `NM_VOTAVEL`, `QT_VOTOS`, `NR_LOCAL_VOTACAO`, `SQ_CANDIDATO`, `NM_LOCAL_VOTACAO`, `DS_LOCAL_VOTACAO_ENDERECO`.
- Na amostra inicial, os registros exibidos indicam geração em 06/10/2026 às 14:03:43, eleição de 2026, código 6257, descrição `Eleição Geral Federal 2026`, data de eleição 04/10/2026 e turno 1. Isso descreve somente as linhas amostradas, não o conteúdo integral do CSV.
- Próxima etapa: repetir o perfilamento sequencial do CSV de aproximadamente 1,05 GB usando `encoding="cp1252"` e `delimiter=";"`, sem carregar o arquivo inteiro na memória e sem regravar ou modificar o original. Apurar total de registros, turnos, cargos, UFs, eleição/data e votos por candidato no segundo turno presidencial. Ainda não há resultado desse perfilamento.
