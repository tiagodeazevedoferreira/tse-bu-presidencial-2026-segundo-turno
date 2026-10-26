# TSE BU Presidencial 2026 — Segundo turno

Projeto separado para ingestão, validação, consolidação e análise dos Boletins de Urna (BU) oficiais do segundo turno da eleição presidencial de 2026.

O repositório do primeiro turno permanece independente:
https://github.com/tiagodeazevedoferreira/tse-bu-presidencial-2026

## Estado atual

- [x] Repositório criado e acessível.
- [x] Escopo e regras de integridade documentados.
- [ ] Confirmar e registrar os recursos oficiais de BU do segundo turno e seus hashes.
- [ ] Baixar e inspecionar uma UF piloto.
- [ ] Validar esquema, códigos de votação e campos de data/hora.
- [ ] Adaptar pipeline de download e processamento para o segundo turno.
- [ ] Executar testes automatizados e validação nacional das 27 UFs.
- [ ] Gerar auditoria reproduzível e dashboard independente.
- [ ] Avaliar análises de inferência ecológica como módulo exploratório separado.

**Não há dados do segundo turno processados ou validados neste commit inicial.** A execução nacional só poderá ser declarada concluída depois que a fonte oficial estiver identificada, as 27 UFs forem processadas e a consolidação passar pelas verificações de integridade.

## Fonte oficial

- [Portal de Dados Abertos do TSE — Resultados 2026 - Boletim de Urna](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna)
- [Conjuntos de dados do TSE etiquetados Ano 2026](https://dadosabertos.tse.jus.br/dataset/?tags=Ano+2026)

A página do conjunto de BU informa que o conjunto abrange 1º e 2º turnos, mas a listagem pública consultada nesta etapa exibe recursos identificados como primeiro turno. A disponibilidade, o nome e a estrutura dos arquivos de BU específicos do segundo turno ainda precisam ser confirmados diretamente na fonte. Não reutilizar URLs, sufixos de ZIP, códigos de voto ou hashes do primeiro turno sem validação.

## Regras de integridade

- Usar somente dados oficiais, preservando a URL, data de obtenção e hash de cada arquivo.
- Nunca fabricar linhas de BU nem inferir seções ausentes.
- Não alterar silenciosamente códigos de candidatos ou de votos brancos/nulos.
- Não commitar arquivos ZIP brutos ou grandes dados derivados sem necessidade.
- Preservar os dados do primeiro turno no repositório original.
- Validar chaves de seção, duplicidades, valores negativos, totais, comparecimento, metadados e consistência entre arquivos.
- Processar arquivos grandes em streaming/chunks quando necessário.
- Registrar explicitamente limitações e falhas; ausência de dado não equivale a zero.
- Não declarar conclusão nacional sem cobertura das 27 UFs e consolidação validada.

## Plano de análises

1. **Descritivas por seção, município e UF:** votos, comparecimento, abstenção e cobertura dos arquivos.
2. **Emissão e recebimento dos BUs:** somente se os campos e sua semântica forem confirmados no arquivo oficial do segundo turno.
3. **Comparação entre turnos:** alinhar seções por chave oficial e documentar seções ausentes, mudanças de local e diferenças de eleitorado/comparecimento.
4. **Inferência ecológica exploratória:** avaliar regressão ecológica de Goodman e o método de inferência ecológica de Gary King apenas se as tabelas agregadas e pressupostos forem apropriados. Não apresentar estimativas como trajetórias observadas de eleitores individuais.

## Inferência ecológica: limites interpretativos

Os BUs são dados agregados por seção, não registros individuais ligando o voto de uma pessoa no primeiro turno ao voto dela no segundo. Portanto, qualquer estimativa de transição individual entre opções de voto será inferencial, dependente de pressupostos e sujeita a incerteza.

A regressão de Goodman pode produzir estimativas fora dos limites possíveis e é sensível a pressupostos sobre homogeneidade/independência entre composição da unidade e comportamento. Métodos de King (EI) modelam a incerteza e impõem limites factíveis, mas também dependem de pressupostos e não recuperam observações individuais inexistentes. O projeto deverá apresentar intervalos, diagnósticos, análises de sensibilidade e limites determinísticos, não apenas estimativas pontuais. Se os pressupostos não puderem ser defendidos, limitar a análise a padrões agregados descritivos.

Referências metodológicas iniciais:
- [King, Rosen, Tanner — Ecological Inference](https://www.cambridge.org/core/books/ecological-inference/9ABBC9189A3F2557CDB6120EFF459A6A)
- [Artigo metodológico sobre Goodman e inferência ecológica (Springer)](https://link.springer.com/article/10.1007/s11135-017-0481-z)
- [Ecological inference (revisão em PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC33746/)

## Próxima etapa técnica

Confirmar os recursos e arquivos oficiais de BU do segundo turno. Em seguida, baixar uma UF piloto, verificar o hash publicado pelo TSE, inspecionar cabeçalhos e códigos reais e só então adaptar o pipeline. Não presumir que substituir o padrão de arquivo de primeiro turno pelo de segundo turno no downloader seja suficiente.
