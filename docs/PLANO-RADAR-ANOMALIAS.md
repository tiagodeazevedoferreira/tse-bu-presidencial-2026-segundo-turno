# Auditoria da base e plano do Radar de Anomalias

## Objetivo

Auditar a qualidade estrutural do CSV atualmente usado pelo dashboard antes de implementar novos indicadores estatísticos. Esta etapa não modifica o HTML, o CSV original nem a publicação do GitHub Pages.

## Fonte atual identificada

- Arquivo: \`data/NovoArquivoDashboard.csv\`
- Tamanho observado no GitHub: 37.062.857 bytes (aprox. 37,1 MB).
- O código de \`index.html\` baixa o arquivo inteiro com \`fetch()\`, converte a resposta em texto, divide as linhas e cria objetos JavaScript.
- O parser atual transforma campos numéricos vazios ou inválidos em zero. Isso precisa ser corrigido antes de usar os resultados para auditoria estatística.
- A aplicação soma os votos disponíveis por turno, mas a base atual não oferece, pelo que o código declara, todos os campos necessários para validar comparecimento, abstenção, votos brancos/nulos e eleitorado.

## Executar a auditoria local

Requisitos: Python 3.10 ou superior. O script usa apenas a biblioteca padrão.

No PowerShell, a partir da raiz do repositório:

\`\`\`powershell
python .\\tools\\audit_dashboard_csv.py .\\data\\NovoArquivoDashboard.csv --output .\\reports\\auditoria_csv_dashboard.json
\`\`\`

O script lê o CSV em streaming, detecta o delimitador, mapeia os cabeçalhos conhecidos pelo dashboard e gera um relatório JSON. Usa SQLite temporário para verificar chaves de seção duplicadas sem manter todas as chaves em um conjunto Python na memória. O CSV de origem não é alterado.

Se o relatório retornar \`schema_incompativel\`, confira os cabeçalhos registrados no JSON e ajuste os aliases do script antes de interpretar os números. Não renomeie nem regrave a fonte apenas para fazer a auditoria passar.

## Como interpretar o relatório

- **Colunas obrigatórias ausentes:** o esquema real não corresponde ao que o dashboard espera; não prossiga para cálculos até resolver.
- **Chaves duplicadas:** linhas com a mesma UF, município, zona e seção; revisar a origem e a granularidade antes de excluir qualquer registro.
- **Campos numéricos vazios:** são reportados como ausentes, não tratados como zero.
- **Valores numéricos inválidos ou negativos:** conferir no CSV original e na fonte oficial.
- **Votos parciais por turno:** um candidato tem valor e o outro está ausente; distinguir ausência de dado de zero votos.
- **Máximo e soma por campo:** estatísticas descritivas para inspeção, não prova de irregularidade.

O script estrutural não declara um dado fraudulento e não substitui a comparação com uma fonte independente. A comparação com BU oficial é executada separadamente por `tools/audit_dashboard_against_tse_bu.py`.

## Decisões técnicas preliminares

1. Manter o CSV como fonte de referência, sem substituí-lo.
2. Corrigir a semântica dos campos: zero é zero; vazio, inválido e turno ausente são estados diferentes.
3. Gerar um formato derivado somente depois que a auditoria confirmar o esquema e as regras de interpretação.
4. Medir CSV atual versus JSON gzip e, se necessário, JSON compacto em arrays. Comparar tamanho transferido, tempo até renderização, memória e comportamento em desktop.
5. Não adotar Parquet/DuckDB-WASM até que um teste mostre que a solução simples não atende aos requisitos.
6. Implementar cálculos analíticos num módulo independente da interface, com testes unitários.

## Plano do Radar de Anomalias

### Fase A — integridade e cobertura

- Validar cabeçalhos, delimitador, codificação, campos numéricos e chaves.
- Medir cobertura por turno e número de seções presentes em ambos.
- Preservar ausências como ausências; nunca preencher automaticamente um turno faltante com zero.
- Cruzar dados complementares do TSE somente com identificadores geográficos oficiais e validação de cardinalidade.

### Fase B — métricas descritivas

- Variação absoluta: valor do segundo turno menos o do primeiro.
- Variação percentual: diferença dividida pelo valor inicial; se o inicial for zero, resultado não calculável.
- Participação sobre a soma dos votos dos dois candidatos, explicitamente identificada como participação relativa, não necessariamente participação oficial sobre todos os votos válidos.
- Variação da participação em pontos percentuais e mudança da margem entre candidatos.
- Exibir os totais e a cobertura usada em cada cálculo.

### Fase C — detecção estatística

- Começar por regras transparentes e casos extremos.
- Comparar localidades com grupos de referência comparáveis e documentados.
- Testar mediana e desvio absoluto mediano (MAD), com tratamento para MAD igual a zero.
- Avaliar tamanho da seção, cobertura entre turnos, diferenças de participação e multiplicidade dos testes.
- Calibrar limiares usando a distribuição observada; não assumir que uma variação grande é impossível apenas por parecer incomum.

### Fase D — interface investigativa

- Ranking de alertas com filtros geográficos existentes.
- Gráfico de dispersão entre mudanças dos candidatos.
- Detalhamento até seção com valores originais e motivo do alerta.
- Exportação CSV dos casos filtrados.
- Classificações distintas: inconsistência objetiva, anomalia estatística e caso para investigação.

## Critérios para avançar

A auditoria estrutural do CSV já foi executada localmente. Ela verifica a consistência interna da base, mas não substitui a comparação independente dos votos com os boletins de urna do TSE. Essa comparação foi iniciada com um piloto do segundo turno em Roraima; a validação nacional e a comparação do primeiro turno continuam pendentes. Antes de alterar o parser de produção ou migrar o formato, registrar os relatórios, resolver incompatibilidades de esquema e confirmar que as somas agregadas correspondem ao comportamento esperado do dashboard atual.

Anomalias estatísticas são sinais para conferência, não prova de fraude. Comparações agregadas entre turnos não identificam o caminho individual de votos.

## Auditoria independente de votos - piloto de Roraima

**Estado em 29/10/2026:** piloto concluído sem divergências nos votos comparáveis.

- **Fonte:** https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna
- **Arquivo:** `bweb_2t_RR_261020260742.zip`, segundo turno de Roraima.
- **Integridade:** SHA-512 publicado pelo TSE conferido com o arquivo baixado.
- **Script:** `tools/audit_dashboard_against_tse_bu.py`.
- **Relatório:** `reports/auditoria_bu_dashboard_RR.json`.
- **Chaves:** 1.519 chaves geográficas no dashboard, 1.519 chaves de BU e 1.519 em comum; nenhuma chave exclusiva e nenhuma chave duplicada no dashboard.
- **Votos:** zero divergências para Lula e Flávio nos registros comparáveis; nenhum valor de voto inválido identificado no dashboard.
- **Ausências nominais:** oito seções sem registro nominal de Flávio no arquivo de BU. O zero é usado somente para a comparação de votos, sem alterar o CSV original. A seção 63 de Uiramutã contém indicação de agregação de seções e requer cautela interpretativa.
- **Testes automatizados:** seis testes passaram, incluindo comparação com ZIP sintético e rejeição de hash divergente.

### Limites e próximos passos

O resultado valida somente a comparação dos votos do segundo turno no piloto de Roraima. Não comprova cobertura nacional, não valida o primeiro turno e não constitui, por si só, evidência de fraude ou de comportamento individual de eleitores.

1. Revisar o código, o relatório e os testes do piloto.
2. Confirmar e processar os arquivos oficiais das demais UFs, preservando hashes, esquemas e resultados por UF.
3. Planejar e executar separadamente a comparação do primeiro turno.
4. Manter ausências, zeros e valores inválidos como situações distintas.
5. Declarar validação nacional somente após concluir e revisar a cobertura das 27 UFs.
