# Painel Institucional PROGRAD – UFT

Painel analítico da Pró-Reitoria de Graduação da Universidade Federal do Tocantins, criado para consultar e explorar informações consolidadas de servidores docentes e técnico-administrativos.

## Visão geral

O painel apresenta os dados de forma interativa, permitindo combinar filtros e acompanhar automaticamente os indicadores e gráficos relacionados ao perfil funcional, acadêmico e institucional dos servidores.

Os dados são carregados a partir do arquivo `perfil.xlsx`, considerando as abas de docentes e técnicos. Durante o carregamento, o painel consolida as categorias, remove registros duplicados, calcula a idade e cria classificações para titulação, campus, forma de ingresso e carga horária.

## Principais funcionalidades

- Filtros combinados por:
  - categoria funcional (docente ou técnico);
  - sexo/gênero;
  - qualificação e titulação;
  - carga horária ou regime de trabalho;
  - situação funcional;
  - regime jurídico;
  - forma de ingresso;
  - campus universitário.
- Indicadores gerais atualizados conforme os filtros selecionados, incluindo quantidade de registros, docentes, técnicos, servidores ativos, níveis de titulação e desvios de lotação.
- Visualizações interativas para apoiar a análise e a comparação entre grupos.
- Busca textual na tabela consolidada, permitindo localizar registros por cargo, campus, situação ou outros campos exibidos.
- Download da base filtrada em formato CSV.
- Identificação de registros duplicados removidos durante o processamento.
- Interface com identidade visual institucional da UFT e adaptação para diferentes tamanhos de tela.

## Áreas de análise

O painel está organizado nas seguintes abas:

1. **Qualificação** – distribuição da titulação por categoria, composição por sexo, principais cargos e índice de qualificação do corpo docente (IQCD).
2. **Lotação & Campus** – distribuição por campus, relação entre campus e categoria, titulação por campus e principais unidades de exercício.
3. **Regime & Situação** – regimes jurídicos, situação funcional e comparações entre docentes e técnicos.
4. **Perfil Etário** – distribuição de idades, faixas etárias e estatísticas por categoria.
5. **Desvio & Ingresso** – análise de possíveis divergências entre lotação oficial e lotação vinculada, formas de ingresso e carga horária.
6. **Tabela & Download** – consulta da base consolidada após os filtros, busca textual e exportação dos dados filtrados.

## Uso

Para iniciar o painel no Windows, execute `iniciar_dashboard.bat` ou rode o aplicativo a partir da pasta do projeto. Depois, acesse o endereço local informado na inicialização, normalmente:

```text
http://localhost:8501
```

O botão **Entrar** está reservado para uma futura área de acesso restrito e, atualmente, apenas informa que essa funcionalidade está em desenvolvimento.

## Geração de relatório

O arquivo `gerar_relatorio.py` automatiza a abertura do painel e gera uma versão em PDF e uma imagem completa do dashboard, salvas como:

- `Dashboard_Institucional.pdf`
- `Dashboard_Institucional.png`

## Arquivos principais

- `pai.py` – aplicação principal do painel.
- `header_menu.py` – ajuste do posicionamento do controle de abertura da barra lateral.
- `perfil.xlsx` – base de dados utilizada pelo painel.
- `gerar_relatorio.py` – geração automatizada de PDF e imagem. (Em desenvolvimento)
- `iniciar_dashboard.bat` – atalho para iniciar o painel no Windows.
