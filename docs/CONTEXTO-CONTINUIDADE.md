# Contexto de continuidade — segundo turno 2026

## Repositórios
- Primeiro turno (preservar sem alterações por este projeto): https://github.com/tiagodeazevedoferreira/tse-bu-presidencial-2026
- Segundo turno: https://github.com/tiagodeazevedoferreira/tse-bu-presidencial-2026-segundo-turno

## Estado confirmado
- Repositório do segundo turno existe, público, branch padrão `main`.
- README inicial atualizado com escopo, regras de integridade, plano de análise e limitações da inferência ecológica.
- Commit inicial de documentação: `ab4e0cac4ca30396fa9cfc692ea21f6a0b4cf1ca`.
- Nenhum pipeline ou resultado de BU do segundo turno foi criado ou validado até agora.

## Fonte oficial a verificar
- Dataset: https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna
- Catálogo Ano 2026: https://dadosabertos.tse.jus.br/dataset/?tags=Ano+2026
- Na consulta realizada em 26/10/2026, a página de BU descreve cobertura de 1º e 2º turnos, mas os recursos visíveis retornados pela página estavam identificados como primeiro turno. Não supor que o recurso de segundo turno esteja disponível sob o mesmo nome, URL ou esquema. Verificar também hashes SHA2 publicados pelo TSE.
- O catálogo mostra também o conjunto “Resultados 2026 - Arquivos transmitidos para totalização”, descrito como abrangendo 1º e 2º turnos e considerando arquivos na situação “Totalizado”. Pode ser uma fonte complementar para auditoria do fluxo, mas não substitui automaticamente o conjunto de BU por seção; inspecionar seu esquema e documentação antes de usar.

## Próximas tarefas, em ordem
1. Localizar e confirmar a URL oficial do BU do segundo turno, incluindo os arquivos/hash por UF.
2. Baixar uma UF piloto e validar SHA2, cabeçalhos, codificação, delimitador, códigos de cargo/votação e campos temporais.
3. Inspecionar mudanças no schema e nos códigos de voto antes de adaptar scripts do primeiro turno.
4. Criar testes com fixtures oficiais pequenas, sem fabricar dados eleitorais.
5. Implementar download e processamento separados, com paths e nomes explícitos do segundo turno.
6. Validar uma UF piloto, depois as 27 UFs, consolidação nacional e auditoria machine-readable.
7. Só depois publicar dashboard e avaliar modelos estatísticos.

## Inferência ecológica
- Goodman e Gary King/EI são candidatos metodológicos exploratórios para analisar margens agregadas, não registros de votos individuais.
- Uma comparação entre turnos por seção não revela diretamente como cada eleitor mudou de opção. Turnout, abstenção, mudanças de seção/local e composição da população podem alterar margens.
- Antes de ajustar modelos, definir unidade de análise, tabelas de margens, universo/população, pressupostos e estimando. Incluir limites determinísticos, incerteza, diagnósticos e sensibilidade. Não apresentar transições estimadas como observações factuais individuais.
- Referências iniciais estão no README.

## Regras permanentes
- Não inventar linhas ou seções ausentes; não transformar ausência em zero.
- Não alterar silenciosamente códigos de votos.
- Não commitar ZIPs brutos.
- Registrar URL de origem, data/hora de captura, hash e versão do esquema.
- Não declarar validação nacional sem 27 UFs, chaves únicas, totais consistentes e auditoria concluída.
