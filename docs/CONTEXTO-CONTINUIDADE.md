# Contexto de continuidade — segundo turno 2026

## Repositórios
- Primeiro turno (preservar sem alterações por este projeto): https://github.com/tiagodeazevedoferreira/tse-bu-presidencial-2026
- Segundo turno: https://github.com/tiagodeazevedoferreira/tse-bu-presidencial-2026-segundo-turno

## Decisão de escopo
- Reproduzir a arquitetura do primeiro turno no repositório separado do segundo turno.
- Não implementar regressão de Goodman, método de King/EI ou outros modelos de inferência ecológica.
- Limitar as análises a dados observados e comparações descritivas, documentando limites de cobertura entre turnos.
- Não alterar o repositório original do primeiro turno.

## Estado confirmado em 26/10/2026
- Repositório do segundo turno existe, público, branch padrão `main`.
- README e este documento de continuidade estão versionados.
- Nenhum script, pipeline, arquivo de BU do segundo turno ou resultado processado foi criado/validado até agora.
- Foram inspecionados no repositório original `scripts/download_bu.py`, `scripts/process_bu.py` e `scripts/generate_table.py` para entender a arquitetura a replicar.

## Fonte oficial e resultado da consulta
- Dataset oficial: https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna
- Catálogo Ano 2026: https://dadosabertos.tse.jus.br/dataset/?tags=Ano+2026
- A página oficial informa que o conjunto cobre o primeiro e o segundo turnos e é atualizado após cada turno. Entretanto, a listagem de recursos acessível na consulta de 26/10/2026 ainda mostrava recursos rotulados como “Primeiro turno”.
- A URL/nome do recurso de BU do segundo turno e seu hash não estão confirmados. Não fabricar sufixos, não presumir URL de ZIP e não começar processamento com base em nomes de arquivo conjecturados.
- O próximo bloqueio técnico é confirmar a publicação oficial do recurso do segundo turno ou identificar a forma oficial equivalente de download por seção.

## Arquitetura a replicar após confirmar a fonte
1. Download por UF, com retentativas, validação de arquivo e registro de origem/hash.
2. Processamento em chunks e armazenamento temporário SQLite para evitar carregar arquivos inteiros em memória.
3. Mapeamento de códigos de votação somente após inspeção da fonte de segundo turno.
4. Saídas CSV por UF e consolidação nacional por seção.
5. Auditoria de chaves únicas, cobertura das 27 UFs, valores negativos, totais de votos, comparecimento, eleitorado e consistência de metadados.
6. Testes automatizados e validação da UF piloto antes da execução nacional.

## Próximas tarefas, em ordem
1. Confirmar a URL oficial do BU do segundo turno, arquivos por UF e hashes SHA2.
2. Baixar uma UF piloto e inspecionar cabeçalhos, codificação, delimitador, esquema e códigos reais.
3. Adaptar downloader, processador e consolidador em scripts separados do primeiro turno.
4. Criar testes com fixtures oficiais pequenas; nunca fabricar dados eleitorais para simular resultados.
5. Validar a UF piloto e comparar os totais com uma fonte oficial independente quando houver granularidade compatível.
6. Processar as 27 UFs, gerar consolidação e auditoria machine-readable.
7. Só depois considerar dashboard ou análises adicionais descritivas.

## Regras permanentes
- Não inventar linhas de BU nem inferir seções ausentes; não converter ausência em zero.
- Não alterar silenciosamente códigos de voto.
- Não commitar ZIPs brutos.
- Registrar URL, data/hora de captura, hash e versão do esquema.
- Não declarar validação nacional sem 27 UFs, chaves únicas, totais consistentes e auditoria concluída.
