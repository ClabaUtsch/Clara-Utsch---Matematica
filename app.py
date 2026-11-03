import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Cuidado em Dados | Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PASTA_PROJETO = Path(__file__).parent
CAMINHO_DADOS = PASTA_PROJETO / "data" / "dados_demonstrativos.csv"

CORES = {
    "Mulheres": "#A64D79",
    "Homens": "#477A91",
    "fundo": "#FFF9FC",
    "texto": "#382D35",
}

st.markdown(
    """
    <style>
    .stApp { background-color: #fffafd; color: #382d35; }
    [data-testid="stSidebar"] { background-color: #f7edf3; }
    .titulo {font-size: 2.35rem; font-weight: 750; color: #713653; margin-bottom: .15rem;}
    .subtitulo {font-size: 1rem; color: #74616d; margin-bottom: 1.4rem;}
    .kpi {background: #ffffff; border: 1px solid #eedce6; border-radius: 13px;
          padding: 17px 18px; min-height: 112px;}
    .kpi-label {font-size: .88rem; color: #74616d;}
    .kpi-value {font-size: 1.8rem; font-weight: 750; color: #713653; margin-top: 5px;}
    .kpi-help {font-size: .76rem; color: #8a7882; margin-top: 2px;}
    .noticia {background: white; border: 1px solid #eedce6; border-radius: 13px;
              padding: 14px; min-height: 220px;}
    .noticia a {color: #713653; font-weight: 700; text-decoration: none;}
    .aviso {background: #fff4df; border-left: 5px solid #d99b39; padding: 12px 15px;
            border-radius: 7px; color: #61471f;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 2. FUNÇÕES DE LEITURA, PADRONIZAÇÃO E VALIDAÇÃO
# ==============================================================================
COLUNAS_OBRIGATORIAS = ["estado", "faixa_etaria", "ano", "sexo", "horas_semanais"]

@st.cache_data
def carregar_arquivo(arquivo, nome_arquivo):
    """Lê arquivos CSV ou Excel enviados pelo usuário."""
    extensao = Path(nome_arquivo).suffix.lower()
    if extensao == ".csv":
        try:
            return pd.read_csv(arquivo, sep=None, engine="python")
        except UnicodeDecodeError:
            arquivo.seek(0)
            return pd.read_csv(arquivo, sep=None, engine="python", encoding="latin-1")
    if extensao in [".xlsx", ".xls"]:
        return pd.read_excel(arquivo)
    raise ValueError("Formato não suportado. Envie um arquivo CSV, XLSX ou XLS.")


def padronizar_colunas(df):
    """Padroniza nomes de colunas e valida a estrutura recebida."""
    df = df.copy()
    df.columns = (
        df.columns.astype(str).str.strip().str.lower()
        .str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("utf-8")
        .str.replace(" ", "_")
    )
    aliases = {
        "uf": "estado",
        "sigla": "estado",
        "faixa_etaria": "faixa_etaria",
        "idade": "faixa_etaria",
        "grupo_etario": "faixa_etaria",
        "year": "ano",
        "sexo_biologico": "sexo",
        "horas": "horas_semanais",
        "media_horas": "horas_semanais",
        "horas_por_semana": "horas_semanais",
    }
    df = df.rename(columns={c: aliases.get(c, c) for c in df.columns})
    faltantes = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if faltantes:
        raise ValueError(
            "Não encontrei todas as colunas necessárias. "
            f"Colunas ausentes: {', '.join(faltantes)}. "
            f"Esperado: {', '.join(COLUNAS_OBRIGATORIAS)}."
        )

    df["estado"] = df["estado"].astype(str).str.strip().str.upper()
    df["faixa_etaria"] = df["faixa_etaria"].astype(str).str.strip()
    df["sexo"] = df["sexo"].astype(str).str.strip().str.capitalize()
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    df["horas_semanais"] = pd.to_numeric(
        df["horas_semanais"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    )
    df = df.dropna(subset=COLUNAS_OBRIGATORIAS)
    df["ano"] = df["ano"].astype(int)
    df = df[df["horas_semanais"].between(0, 168)]
    df = df[df["sexo"].isin(["Mulheres", "Homens"])]
    if df.empty:
        raise ValueError("O arquivo não possui registros válidos após a limpeza.")
    return df


# ==============================================================================
# 3. CARREGAMENTO DA BASE PADRÃO OU DO UPLOAD
# ==============================================================================
st.sidebar.title("📊 Cuidado em Dados")
st.sidebar.caption("Painel de análise social")
arquivo_enviado = st.sidebar.file_uploader(
    "Enviar uma base de dados",
    type=["csv", "xlsx", "xls"],
    help="A base deve conter estado, faixa_etaria, ano, sexo e horas_semanais.",
)

origem_dos_dados = "Base demonstrativa simulada"
try:
    if arquivo_enviado is not None:
        dados_brutos = carregar_arquivo(arquivo_enviado, arquivo_enviado.name)
        dados = padronizar_colunas(dados_brutos)
        origem_dos_dados = f"Arquivo enviado: {arquivo_enviado.name}"
    else:
        dados_brutos = pd.read_csv(CAMINHO_DADOS)
        dados = padronizar_colunas(dados_brutos)
except Exception as erro:
    st.error(f"Não foi possível carregar os dados: {erro}")
    st.info("Confira o modelo de colunas no arquivo README.md e envie a planilha novamente.")
    st.stop()

# ==============================================================================
# 4. FILTROS DA BARRA LATERAL
# ==============================================================================
st.sidebar.divider()
st.sidebar.subheader("Filtros")

estados_disponiveis = sorted(dados["estado"].unique())
anos_disponiveis = sorted(dados["ano"].unique())
faixas_disponiveis = sorted(dados["faixa_etaria"].unique())

estados_selecionados = st.sidebar.multiselect(
    "Estados", estados_disponiveis, default=estados_disponiveis
)
faixas_selecionadas = st.sidebar.multiselect(
    "Faixa etária", faixas_disponiveis, default=faixas_disponiveis
)
anos_selecionados = st.sidebar.multiselect(
    "Ano", anos_disponiveis, default=anos_disponiveis
)

dados_filtrados = dados[
    dados["estado"].isin(estados_selecionados)
    & dados["faixa_etaria"].isin(faixas_selecionadas)
    & dados["ano"].isin(anos_selecionados)
].copy()

# ==============================================================================
# 5. CABEÇALHO E INDICADORES (KPIs)
# ==============================================================================
st.markdown('<div class="titulo">Cuidado em Dados</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitulo">Carga mental feminina, trabalho doméstico e economia do cuidado</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="aviso"><b>Origem dos dados:</b> {origem_dos_dados}. '
    "A base que acompanha o projeto é simulada para demonstração; "
    "não representa estimativas oficiais.</div>",
    unsafe_allow_html=True,
)
st.write("")

if dados_filtrados.empty:
    st.warning("Nenhum registro corresponde aos filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

media_geral = dados_filtrados["horas_semanais"].mean()
medias_sexo = dados_filtrados.groupby("sexo")["horas_semanais"].mean()
media_mulheres = medias_sexo.get("Mulheres", 0)
media_homens = medias_sexo.get("Homens", 0)
diferenca = media_mulheres - media_homens
total_registros = len(dados_filtrados)

k1, k2, k3, k4 = st.columns(4)
indicadores = [
    (k1, "Média geral semanal", f"{media_geral:.1f} h", "Horas por pessoa na base filtrada"),
    (k2, "Média – mulheres", f"{media_mulheres:.1f} h", "Horas semanais"),
    (k3, "Média – homens", f"{media_homens:.1f} h", "Horas semanais"),
    (k4, "Diferença entre médias", f"{diferenca:+.1f} h", "Mulheres menos homens"),
]
for coluna, rotulo, valor, apoio in indicadores:
    with coluna:
        st.markdown(
            f'<div class="kpi"><div class="kpi-label">{rotulo}</div>'
            f'<div class="kpi-value">{valor}</div><div class="kpi-help">{apoio}</div></div>',
            unsafe_allow_html=True,
        )

st.caption(f"Registros considerados: {total_registros:,}".replace(",", "."))

# ==============================================================================
# 6. GRÁFICOS INTERATIVOS
# ==============================================================================
st.divider()
st.subheader("Comparação das horas semanais por sexo e estado")
por_estado = (
    dados_filtrados.groupby(["estado", "sexo"], as_index=False)["horas_semanais"]
    .mean()
)
if not por_estado.empty:
    grafico_estado = px.bar(
        por_estado,
        x="estado",
        y="horas_semanais",
        color="sexo",
        barmode="group",
        color_discrete_map=CORES,
        labels={
            "estado": "Estado",
            "horas_semanais": "Média de horas por semana",
            "sexo": "Sexo",
        },
        template="plotly_white",
    )
    grafico_estado.update_layout(legend_title_text="", xaxis_title="", yaxis_title="Horas semanais")
    st.plotly_chart(grafico_estado, use_container_width=True)

col_esquerda, col_direita = st.columns(2)
with col_esquerda:
    st.subheader("Distribuição das horas (boxplot)")
    boxplot = px.box(
        dados_filtrados,
        x="sexo",
        y="horas_semanais",
        color="sexo",
        color_discrete_map=CORES,
        points="outliers",
        labels={"sexo": "Sexo", "horas_semanais": "Horas semanais"},
        template="plotly_white",
    )
    boxplot.update_layout(showlegend=False, xaxis_title="", yaxis_title="Horas semanais")
    st.plotly_chart(boxplot, use_container_width=True)

with col_direita:
    st.subheader("Média por faixa etária")
    por_idade = (
        dados_filtrados.groupby(["faixa_etaria", "sexo"], as_index=False)["horas_semanais"]
        .mean()
    )
    grafico_idade = px.bar(
        por_idade,
        x="faixa_etaria",
        y="horas_semanais",
        color="sexo",
        barmode="group",
        color_discrete_map=CORES,
        labels={
            "faixa_etaria": "Faixa etária",
            "horas_semanais": "Média de horas",
            "sexo": "Sexo",
        },
        template="plotly_white",
    )
    grafico_idade.update_layout(legend_title_text="", xaxis_title="", yaxis_title="Horas semanais")
    st.plotly_chart(grafico_idade, use_container_width=True)

with st.expander("Visualizar os dados filtrados"):
    st.dataframe(dados_filtrados, use_container_width=True, hide_index=True)
    st.download_button(
        "Baixar dados filtrados em CSV",
        dados_filtrados.to_csv(index=False).encode("utf-8-sig"),
        file_name="dados_cuidado_filtrados.csv",
        mime="text/csv",
    )

# ==============================================================================
# 7. CONTEÚDO INFORMATIVO E REPORTAGENS
# ==============================================================================
def imagem_svg_base64(nome_arquivo):
    caminho = PASTA_PROJETO / "assets" / nome_arquivo
    conteudo = caminho.read_bytes()
    return base64.b64encode(conteudo).decode("utf-8")

st.divider()
st.header("Entenda o tema")
st.write(
    "A economia do cuidado reúne atividades essenciais para a manutenção da vida, "
    "como cuidar de crianças e idosos, preparar alimentos e organizar a rotina doméstica. "
    "Quando essas tarefas e o planejamento associado ficam concentrados em uma pessoa, "
    "também existe uma carga mental que nem sempre aparece nas estatísticas."
)

n1, n2 = st.columns(2)
with n1:
    st.image(str(PASTA_PROJETO / "assets" / "carga_mental.svg"), use_container_width=True)
    st.subheader("Carga mental feminina")
    st.write(
        "É o esforço de lembrar, antecipar, planejar e coordenar tarefas e responsabilidades "
        "do cotidiano. A reportagem aborda como essa organização invisível pode se distribuir "
        "de forma desigual."
    )
    st.markdown(
        "[Ler reportagem – Drauzio Varella](https://drauziovarella.uol.com.br/mulher/carga-mental-feminina-por-que-as-mulheres-estao-exaustas/)"
    )
with n2:
    st.image(str(PASTA_PROJETO / "assets" / "economia_cuidado.svg"), use_container_width=True)
    st.subheader("Economia do cuidado")
    st.write(
        "O trabalho doméstico e de cuidado sustenta famílias e a sociedade, mesmo quando "
        "não é remunerado. A reportagem discute a invisibilidade econômica dessas atividades."
    )
    st.markdown(
        "[Ler reportagem – O POVO](https://mais.opovo.com.br/reportagens-especiais/mulheres-e-cuidado-economia-sociedade/2024/06/25/economia-do-cuidado-um-trabalho-invisivel-e-nao-remunerado-das-mulheres.html)"
    )

st.subheader("Dados e contexto")
st.markdown(
    "- [IBGE – Mulheres dedicavam 10,4 horas semanais a mais que os homens (dados de 2019)]"
    "(https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/27877-em-media-mulheres-dedicam-10-4-horas-por-semana-a-mais-que-os-homens-aos-afazeres-domesticos-ou-ao-cuidado-de-pessoas)\n"
    "- [Agência Brasil – Trabalho de cuidado e desigualdade de gênero (2026)]"
    "(https://agenciabrasil.ebc.com.br/economia/noticia/2026-05/trabalho-de-cuidado-mulheres-tem-escala-7x0-diz-pesquisadora)\n"
    "- [MDS – Política de cuidados e corresponsabilidade (2025/2026)]"
    "(https://www.gov.br/mds/pt-br/noticias-e-conteudos/desenvolvimento-social/noticias-desenvolvimento-social/mulheres-dedicam-quase-10-horas-a-mais-por-semana-do-que-os-homens-a-cuidados-nao-remunerados)"
)

# ==============================================================================
# 8. LEITURA DOS CENÁRIOS PARA APRESENTAÇÃO
# ==============================================================================
st.divider()
st.header("Leitura dos cenários")
st.markdown(
    f"""
    - **Diferença de médias:** no recorte selecionado, a diferença entre mulheres e homens
      é de **{diferenca:.1f} horas semanais**.
    - **Comparação territorial:** observe no gráfico de barras quais estados apresentam
      maiores médias e se a distância entre os grupos se repete.
    - **Distribuição:** o boxplot permite comparar mediana, dispersão e valores extremos,
      sem reduzir a análise apenas à média.
    - **Faixa etária:** use o gráfico por idade para verificar se a distribuição das
      responsabilidades muda entre os grupos.
    """
)
st.info(
    "Importante para a apresentação: os resultados deste painel dependem da base carregada. "
    "Não interprete dados simulados como resultados oficiais nem como prova de causalidade."
)

st.caption(
    "Cuidado em Dados • Projeto educacional de análise de dados • "
    "Tecnologias: Python, Streamlit, Pandas e Plotly"
)
