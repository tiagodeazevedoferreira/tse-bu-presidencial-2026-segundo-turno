# Dashboard de comparação entre turnos — Eleições 2026

Este dashboard estático do GitHub Pages usa `data/NovoArquivoDashboard.csv`, uma base delimitada por ponto e vírgula que contém os votos de Lula e Flávio Bolsonaro por seção nos dois turnos.

## O que o dashboard mostra

- Votos de Lula e Flávio Bolsonaro no 1º e no 2º turno.
- Variação absoluta e percentual entre os turnos.
- Participação de cada candidato na soma dos votos dos dois candidatos.
- Filtros e detalhamento por região, UF, município, local de votação, zona e seção.
- Comparação em tabelas e gráficos.

## Limitações da base atual

O CSV atual fornece UF, nome do município, zona, seção, descrição do local e votos dos dois candidatos nos dois turnos. Não fornece códigos oficiais de município ou local de votação, endereço, votos brancos ou nulos. Por isso, esses campos não são apresentados como se estivessem disponíveis. Município e local são identificados pelo texto presente no arquivo.

A base é carregada pelo navegador diretamente do CSV publicado pelo GitHub Pages. O arquivo de origem no repositório é mantido em `data/NovoArquivoDashboard.csv`; não é necessário gerar o JSON gzip antigo para esta versão do dashboard.

## Publicação

O workflow `.github/workflows/pages-comparacao-turnos.yml` publica `index.html` e copia `data/NovoArquivoDashboard.csv` para o site. Alterações no HTML, no workflow ou no CSV acionam a publicação.

## Definições

- Variação absoluta = votos do 2º turno menos votos do 1º turno.
- Variação percentual = variação absoluta dividida pelos votos do 1º turno, vezes 100. Se o valor inicial for zero, a porcentagem é mostrada como não calculável.
- Participação do candidato = seus votos divididos pela soma dos votos de Lula e Flávio no mesmo turno.
- A diferença entre turnos é uma comparação agregada; não demonstra transferência individual de votos.
