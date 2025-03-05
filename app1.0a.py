import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
import logging
import os
import sys

# Configuração da página (sempre wide e título personalizado)
st.set_page_config(
    layout="wide",  # Abre sempre no modo wide
    page_title="Laudos SecEst",  # Título da aba do navegador
    page_icon="📊",  # Ícone da aba do navegador
)

# Opcional: reduz a verbosidade dos logs do Streamlit
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Configuração da conexão com o banco de dados (apenas leitura)
CONNECTION_STRING = (
    "postgresql://neondb_owner:npg_8sDOa5NqKXt@"
    "ep-patient-art-a6lqv00a-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"
)
engine = create_engine(CONNECTION_STRING)

def gerar_graficos():
    df = pd.read_sql_query("SELECT * FROM laudos", engine)
    if df.empty:
        st.error("⚠️ Não há dados para gerar gráficos.")
        return

    try:
        df['ano'] = df['ano'].astype(int)
    except ValueError:
        st.error("⚠️ A coluna 'ano' possui valores não numéricos.")

    fig, axes = plt.subplots(2, 3, figsize=(24, 12))
    fig.suptitle("Seção de Estatísticas - Balística - SecTec/Ccrim", fontsize=20, fontweight='bold')
    axes = axes.flatten()

    opm_counts = df['opm'].value_counts()
    axes[0].pie(opm_counts, labels=opm_counts.index, autopct='%1.1f%%', startangle=140)
    axes[0].set_title('Laudos por OPM')

    ano_counts = df.groupby('ano').size().sort_index()
    axes[1].plot(ano_counts.index, ano_counts.values, marker='o', linestyle='-')
    axes[1].set_title('Laudos por Ano')

    perito_counts = df['perito_relator'].value_counts()
    axes[2].barh(perito_counts.index, perito_counts.values)
    axes[2].set_title('Laudos por Perito')

    sns.countplot(ax=axes[3], data=df, x='marca_arma', order=df['marca_arma'].value_counts().index)
    axes[3].set_title('Laudos por Marca')
    axes[3].set_xlabel('Marca')
    axes[3].set_ylabel('Quantidade')
    for label in axes[3].get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')

    modelo_counts = df['modelo_arma'].value_counts()
    axes[4].barh(modelo_counts.index, modelo_counts.values)
    axes[4].set_title('Laudos por Modelo')

    exame_counts = df['descricao_exame'].value_counts()
    wedges, texts, autotexts = axes[5].pie(exame_counts, labels=exame_counts.index, autopct='%1.1f%%', startangle=90)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    axes[5].add_artist(centre_circle)
    axes[5].set_title('Laudos por Exame')

    sns.despine()
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    st.pyplot(fig)

def listar_laudos_em_tramitacao_aberta():
    query = text("""
            SELECT l.numero_laudo, l.ano, l.opm, 
                   t.responsavel_atual, t.data_recebimento, t.observacao
              FROM laudos l
              JOIN tramitacoes t ON l.id = t.laudo_id
             WHERE t.data_conclusao IS NULL
             ORDER BY t.data_recebimento ASC
        """)
    df_abertos = pd.read_sql_query(query, engine)

    if df_abertos.empty:
        st.error("⚠️ Nenhum laudo com tramitação em aberto encontrado.")
    else:
        if 'data_recebimento' in df_abertos.columns:
            df_abertos['data_recebimento'] = pd.to_datetime(df_abertos['data_recebimento'], errors='coerce')
            df_abertos['data_recebimento'] = df_abertos['data_recebimento'].dt.strftime("%d/%m/%Y %H:%M:%S")
        st.subheader("Laudos - Tramitação")
        st.dataframe(df_abertos)

if __name__ == '__main__':
    gerar_graficos()
    listar_laudos_em_tramitacao_aberta()
