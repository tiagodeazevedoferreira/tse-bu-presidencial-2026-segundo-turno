# TSE BU Presidencial 2026 — Segundo turno

Projeto separado para ingestão, validação, consolidação e análise dos Boletins de Urna (BU) oficiais do segundo turno da eleição presidencial de 2026.

O repositório do primeiro turno permanece independente:
https://github.com/tiagodeazevedoferreira/tse-bu-presidencial-2026

## Estado atual

- [x] Repositório criado e escopo documentado.
- [x] Estratégia definida: reproduzir a arquitetura do primeiro turno, em um repositório separado.
- [x] Decisão metodológica: não implementar Goodman, King/EI ou modelos de inferência ecológica.
- [ ] Confirmar os recursos oficiais de BU do segundo turno e seus hashes.
- [ ] Baixar e inspecionar uma UF piloto.
- [ ] Validar esquema, códigos de votação e campos de data/hora.
- [ ] Adaptar download, processamento incremental, consolidação e testes.
- [ ] Validar nacionalmente as 27 UFs e gerar auditoria reproduzível.

**Ainda não há dados do segundo turno processados ou validados.** A execução nacional só poderá ser declarada concluída depois que a fonte oficial estiver identificada, as 27 UFs forem processadas e a consolidação passar pelas verificações de integridade.

## Fonte oficial e situação da verificação

- [TSE — Resultados 2026: Boletim de Urna](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna)
- [Catálogo TSE — Ano 2026](https://dadosabertos.tse.jus.br/dataset/?tags=Ano+2026)

A página oficial do conjunto de BU afirma que os dados abrangem o 1º e o 2º turnos, mas a listagem de recursos visível na consulta de 26/10/2026 apresenta arquivos identificados como **Primeiro turno**. Portanto, a URL, o nome, a disponibilidade e o esquema dos arquivos de BU do segundo turno ainda não estão confirmados. Não inferir um sufixo de arquivo a partir do primeiro turno nem testar URLs presumidas como se fossem fontes oficiais verificadas.

## Estratégia de implementação

Reproduzir, com paths e nomes específicos do segundo turno, a arquitetura já usada no primeiro turno:

1. Download dos recursos oficiais por UF, com registro da URL de origem e validação do hash SHA2 publicado pelo TSE, quando disponível.
2. Processamento incremental em chunks, persistência temporária em SQLite e agregação por chave oficial de seção.
3. Validação dos campos e códigos observados no arquivo real antes de mapear candidatos, branco e nulo.
4. Geração de CSVs por UF e tabela nacional consolidada.
5. Auditoria de cobertura, duplicidades, valores negativos, somas, comparecimento, eleitorado e consistência entre arquivos.
6. Testes automatizados e execução nacional apenas após validar a UF piloto.

## Regras de integridade

- Usar dados oficiais e registrar URL, data/hora de obtenção, hash e versão do esquema.
- Nunca fabricar linhas de BU nem inferir seções ausentes; ausência não equivale a zero.
- Não alterar silenciosamente códigos de candidatos ou votos brancos/nulos.
- Não commitar ZIPs brutos ou grandes dados derivados sem necessidade.
- Preservar os dados do primeiro turno no repositório original.
- Validar chaves de seção, duplicidades, valores negativos, totais, comparecimento, metadados e consistência entre arquivos.
- Processar arquivos grandes em streaming/chunks quando necessário.
- Não declarar conclusão nacional sem cobertura das 27 UFs e consolidação validada.

## Análises previstas

Somente análises descritivas dos dados observados: votos por seção, município e UF; comparecimento e abstenção; metadados de emissão/recebimento do BU se confirmados no esquema oficial; e comparação descritiva entre turnos após alinhar as chaves de seção e documentar mudanças de cobertura, local e eleitorado. Não estimar trajetórias individuais de eleitores a partir de margens agregadas.

## Próxima etapa técnica

Confirmar o recurso oficial do segundo turno. Em seguida, baixar uma UF piloto, conferir o hash publicado pelo TSE, inspecionar cabeçalhos, codificação, delimitador, códigos de cargo/votação e campos temporais e só então adaptar os scripts do primeiro turno. Não presumir que basta trocar `1t` por `2t` no downloader.
