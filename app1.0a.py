import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
import logging
import os
import sys

# Executa o Streamlit manualmente ao iniciar o executável
if getattr(sys, 'frozen', False):
    os.system(f'streamlit run {sys.executable}')

# Opcional: reduz a verbosidade dos logs do Streamlit
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Configuração da conexão com o banco de dados (apenas leitura)
CONNECTION_STRING = (
    "postgresql://neondb_owner:npg_8sDOa5NqzKXt@"
    "ep-patient-art-a6lqv00a-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"
)
engine = create_engine(CONNECTION_STRING)

def gerar_graficos():
    # Consulta os dados do banco
    df = pd.read_sql_query("SELECT * FROM laudos", engine)
    if df.empty:
        st.error("⚠️ Não há dados para gerar gráficos.")
        return

    # Tenta converter a coluna 'ano' para inteiro
    try:
        df['ano'] = df['ano'].astype(int)
    except ValueError:
        st.error("⚠️ A coluna 'ano' possui valores não numéricos.")
        return

    # Cria uma figura com 6 subplots (2x3) e tamanho 24x12
    fig, axes = plt.subplots(2, 3, figsize=(24, 12))
    fig.suptitle("Seção de Estatísticas - Balística - SecTec/Ccrim", fontsize=20, fontweight='bold')
    axes = axes.flatten()  # Transforma em array 1D

    # Gráfico 1: Laudos por Ano (Line plot) - agora em axes[0]
    ano_counts = df.groupby('ano').size().sort_index()
    axes[0].plot(ano_counts.index, ano_counts.values, marker='o', linestyle='-')
    axes[0].set_title('Laudos por Ano')
    axes[0].set_xlabel('Ano')
    axes[0].set_ylabel('Quantidade')

    # Gráfico 2: Laudos por Perito (Barra Horizontal) - axes[1]
    perito_counts = df['perito_relator'].value_counts()
    axes[1].barh(perito_counts.index, perito_counts.values)
    axes[1].set_title('Laudos por Perito')
    axes[1].set_xlabel('Quantidade')
    axes[1].set_ylabel('Perito')

    # Gráfico 3: Laudos por Marca (Countplot) - axes[2]
    sns.countplot(ax=axes[2], data=df, x='marca_arma', order=df['marca_arma'].value_counts().index)
    axes[2].set_title('Laudos por Marca')
    axes[2].set_xlabel('Marca')
    axes[2].set_ylabel('Quantidade')
    for label in axes[2].get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')

    # Gráfico 4: Laudos por Modelo (Barra Horizontal) - axes[3]
    modelo_counts = df['modelo_arma'].value_counts()
    axes[3].barh(modelo_counts.index, modelo_counts.values)
    axes[3].set_title('Laudos por Modelo')
    axes[3].set_xlabel('Quantidade')
    axes[3].set_ylabel('Modelo')

    # Gráfico 5: Laudos por Exame (Barra Horizontal) - axes[4]
    exame_counts = df['descricao_exame'].value_counts()
    axes[4].barh(exame_counts.index, exame_counts.values)
    axes[4].set_title('Laudos por Exame')
    axes[4].set_xlabel('Quantidade')
    axes[4].set_ylabel('Descrição')

    # Remove o último subplot (axes[5]) para não ficar vazio
    fig.delaxes(axes[5])

    sns.despine()
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Exibe a figura na aplicação Streamlit
    st.pyplot(fig)

def listar_laudos_em_tramitacao_aberta():
    """
    Lista todos os laudos que possuem tramitações em aberto (data_conclusao IS NULL).
    """
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
        # Formata a coluna de data para exibição adequada
        if 'data_recebimento' in df_abertos.columns:
            df_abertos['data_recebimento'] = pd.to_datetime(df_abertos['data_recebimento'], errors='coerce')
            df_abertos['data_recebimento'] = df_abertos['data_recebimento'].dt.strftime("%d/%m/%Y %H:%M:%S")
        st.subheader("Laudos - Tramitação")
        st.dataframe(df_abertos)

if __name__ == '__main__':
    gerar_graficos()
    listar_laudos_em_tramitacao_aberta()

