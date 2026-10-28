# Dashboard de comparação entre turnos — Eleições 2026

Este dashboard é um artefato estático para GitHub Pages. Os votos vêm exclusivamente do arquivo oficial do TSE `votacao_secao_2026_BR.csv`, que contém os dois turnos.

## O que o dashboard mostra

- Big numbers para Lula (13) e Flávio Bolsonaro (22): votos no 1º e no 2º turno, variação absoluta, variação percentual e participação nos votos nominais dos dois candidatos.
- Votos brancos (95) e nulos (96).
- Filtros/drill-down por região, UF, município, local de votação, zona e seção.
- Contagem de seções disponíveis em cada turno e em ambos, para não esconder diferenças de cobertura.
- Exterior (código geográfico `ZZ`) separado das cinco regiões brasileiras.

O arquivo original de 1,58 GB **não deve ser commitado**. O gerador transforma o CSV em um JSON gzip compacto, com apenas os campos necessários para o dashboard.

## Gerar o conjunto de dados no Windows

Requisitos: Python e pandas instalados. Coloque o CSV oficial no diretório de trabalho, ou informe o caminho com `--input`.

No PowerShell, a partir da raiz deste repositório:

```powershell
& $python .\tools\build_turnos_data.py --input "C:\caminho\para\votacao_secao_2026_BR.csv"
```

Se a variável `$python` não estiver definida, substitua `& $python` pelo caminho completo do executável Python.

O script gera:

```text
data/dashboard/votos_turnos_2026.json.gz
```

O processamento lê o CSV em blocos, usa SQLite temporário, valida os códigos de eleição esperados (6257 no 1º turno e 6258 no 2º), mantém a chave de seção e não altera o CSV de origem.

Confira no final:
- tamanho do arquivo compactado;
- número de seções com dados em cada turno e nos dois turnos;
- totais por turno para os códigos 13, 22, 95 e 96.

## Publicação

O workflow `.github/workflows/pages-comparacao-turnos.yml` publica o `index.html` da raiz e copia o arquivo compactado para `data/dashboard/` no artefato do Pages. Este repositório é independente do repositório do primeiro turno.

Para ativar a versão com dados, o arquivo `data/dashboard/votos_turnos_2026.json.gz` precisa estar commitado no repositório. Não inclua o CSV bruto.

## Análise de casos extremos

A visão "Análise de casos extremos" trabalha no nível de seção eleitoral e reaproveita os votos já publicados no JSON do dashboard. O limite inicial é inclusivo: 100 votos.

Tipos de ocorrência:

- **Zero votos contra 100 ou mais no mesmo turno:** Lula = 0 e Flávio >= 100, ou Flávio = 0 e Lula >= 100, avaliados separadamente no 1º e no 2º turno.
- **Mudança entre turnos:** para um mesmo candidato, 0 no 1º turno e >= 100 no 2º, ou >= 100 no 1º turno e 0 no 2º.

Uma seção que satisfaça várias regras aparece uma única vez, com todos os motivos listados. Se o campo v2 for null, o segundo turno é tratado como ausente, nunca como zero; por isso, essa seção não pode satisfazer uma regra de mudança entre turnos nem uma regra de zero no segundo turno. A visão respeita os filtros geográficos existentes e exibe até 500 ocorrências por vez, ordenadas pela maior quantidade de votos observada. O total de ocorrências encontradas é informado separadamente.

Esses critérios são sinalizadores para investigação, não evidência de irregularidade ou de transferência individual de votos. Antes de interpretar um caso, confira os valores originais da seção e a cobertura do turno.

## Definições

- Variação absoluta = votos do 2º turno menos votos do 1º turno.
- Variação percentual = variação absoluta dividida pelos votos do 1º turno, vezes 100. Se o valor inicial for zero, a porcentagem é mostrada como não calculável.
- Participação do candidato = seus votos divididos pela soma dos votos nominais de Lula e Flávio no mesmo turno.
- A diferença entre turnos é uma comparação agregada. Não demonstra transferência individual de votos.
- Seções ausentes em um dos turnos permanecem ausentes; não são preenchidas artificialmente com zero. O dashboard mostra a cobertura de cada turno e o número de seções comuns.
