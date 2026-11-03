# Cuidado em Dados — Dashboard Streamlit

Dashboard educacional para explorar diferenças na distribuição de horas semanais dedicadas a afazeres domésticos e atividades de cuidado.

## Tecnologias
- Python
- Streamlit
- Pandas
- Plotly

## Como executar

1. Instale o Python 3.10 ou superior.
2. Abra o terminal na pasta do projeto.
3. (Opcional, recomendado) Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   ```

   Windows PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

5. Execute o dashboard:

   ```bash
   streamlit run app.py
   ```

## Estrutura esperada para upload

O arquivo CSV ou Excel deve conter estas colunas:

| Coluna | Descrição | Exemplo |
|---|---|---|
| `estado` | Sigla da UF | MG |
| `faixa_etaria` | Grupo de idade | 18 a 29 |
| `ano` | Ano de referência | 2024 |
| `sexo` | Mulheres ou Homens | Mulheres |
| `horas_semanais` | Média semanal em horas | 22.5 |

Também são aceitos alguns nomes alternativos, como `uf` para `estado`, `idade` para `faixa_etaria`, `year` para `ano`, `horas` ou `media_horas` para `horas_semanais`.

## Funcionalidades
- Filtros de estado, faixa etária e ano.
- Indicadores (KPIs) de média geral, médias por sexo e diferença entre médias.
- Gráfico de barras por estado e sexo.
- Boxplot da distribuição de horas semanais.
- Comparação por faixa etária.
- Upload de CSV, XLSX e XLS.
- Exportação dos dados filtrados.
- Seção informativa com reportagens e fontes institucionais.

## Atenção sobre os dados
O arquivo `data/dados_demonstrativos.csv` é **simulado**, criado apenas para que o dashboard abra e possa ser apresentado/testado sem depender de uma base externa. Ele não representa uma pesquisa oficial, não deve ser citado como resultado real e pode ser substituído por dados observados/documentados.

Para análises oficiais, use microdados ou tabelas publicados pelo IBGE e documente ano, população, metodologia e definição de cada variável. O dashboard não calcula automaticamente estimativas populacionais ou ponderações amostrais.

## Organização do projeto

```text
dashboard_carga_mental/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── dados_demonstrativos.csv
└── assets/
    ├── carga_mental.svg
    └── economia_cuidado.svg
```
