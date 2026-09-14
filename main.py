from pathlib import Path
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
#
csv_path = Path(__file__).resolve().parent / "Brasileiro 2024 (Srie A) - Dataset - Final.csv"

df = pd.read_csv(csv_path,header=None)
df.columns = ['Data','Hora','Mandante','Placar','Visitante','Publico','Estadio']

df[['gols_casa', 'gols_visitante']] = df['Placar'].str.split('–', expand=True).astype(int)
df = df.drop(columns=['Placar'])
df['Publico'] = pd.to_numeric(df['Publico'].str.replace(',', '',regex = False), errors='coerce').astype('Int64')
# print(df[['Mandante', 'gols_casa', 'gols_visitante', 'Publico']].head())
print(f"Total de partidas carregadas: {len(df)}")




# Create a SQLite database connection
conn = sqlite3.connect('brasileiro_2024.db')
df.to_sql('Brasileirao', conn, if_exists='replace', index=False)

consulta1 = (
    "Select Mandante, Sum(gols_casa) as Total_Gols_Casa " \
    "From Brasileirao " \
    "Group By Mandante "
    "Order By Total_Gols_Casa desc " \
    "LIMIT 3"
)
df_consulta = pd.read_sql_query(consulta1, conn)
print(df_consulta)


consulta2 = (
    "Select Mandante, Sum(Case When Gols_Casa > Gols_Visitante Then 1 Else 0 End) as Vitorias "\
    ", Sum(Case When Gols_Casa < Gols_Visitante Then 1 Else 0 End) as Derrotas "\
    ", Sum(Case When Gols_Casa = Gols_Visitante Then 1 Else 0 End) as Empates "\
    "From Brasileirao " \
    "Group By Mandante " \
    "LIMIT 3"
)
df_consulta2 = pd.read_sql_query(consulta2, conn)
print(df_consulta2)


consulta3 = (
    "Select Mandante, Visitante, Publico " \
    "From Brasileirao " \
    "Order By Publico desc " \
    "LIMIT 1"
)
df_consulta3 = pd.read_sql_query(consulta3, conn)
print(df_consulta3)


consulta4 = (
    "Select Mandante, gols_casa, gols_visitante, " \
    "(gols_casa + gols_visitante) as Total_Gols " \
    "From Brasileirao " \
    "Order By Total_Gols desc " \
    "LIMIT 1"
)
df_consulta4 = pd.read_sql_query(consulta4, conn)
print(df_consulta4)

consulta5 = (
    "Select Time, Sum(Pontos) as Total_Pontos "
    "From ("
    "Select Mandante as Time, "
    "Case "
    "when gols_casa > gols_visitante then 3 "
    "When gols_casa = gols_visitante then 1 "
    "Else 0 End as Pontos "
    "From Brasileirao "  
    "Union All "
    "Select Visitante as Time, "
    "Case "
    "When gols_visitante > gols_casa then 3 "
    "When gols_visitante = gols_casa then 1 "
    "Else 0 End as Pontos "
    "From Brasileirao "
    ") As Pontos_Temporada "
    "Group By Time " 
    "Order By Total_pontos desc " 
    "Limit 10 "
)

df_consulta5 = pd.read_sql_query(consulta5, conn)
print(df_consulta5)

consulta6 = (
    "Select " \
    "Round(100.0 * Sum(Case When gols_casa > gols_visitante Then 1 Else 0 End) / Count(*), 2) perc_Vitorias_Casa, " \
    "Round(100.0 * Sum(Case When gols_casa < gols_visitante Then 1 Else 0 End) / Count(*), 2) as perc_Vitorias_Visitante, " \
    "Round(100.0 * Sum(Case When gols_casa = gols_visitante Then 1 Else 0 End) / Count(*), 2) as perc_Empates " \
    "From Brasileirao "
)

df_consulta6 = pd.read_sql_query(consulta6, conn)
print(df_consulta6)

consulta7 = (
    "Select Strftime('%m', Data) as Mes, Avg(gols_casa + gols_visitante)as Media_Gols " \
    "From Brasileirao "
    "Group By Mes " 
    "Order By Mes asc "
)

df_consulta7 = pd.read_sql_query(consulta7, conn)
print(df_consulta7)

consulta8 = (
    "Select Mandante, Visitante, gols_casa, gols_visitante " \
    "From Brasileirao "
    "Where (Mandante = 'Flamengo' or Visitante = 'Flamengo') and (Mandante = 'Palmeiras' or Visitante = 'Palmeiras')" \
)

df_consulta8 = pd.read_sql_query(consulta8, conn)
print(df_consulta8)
conn.close()


graficos_dir = Path(__file__).resolve().parent / "graficos"
graficos_dir.mkdir(exist_ok=True)

plt.figure(figsize=(10, 6))          # tamanho do gráfico
sns.barplot(data=df_consulta5, x='Time', y='Total_Pontos')  # tipo de gráfico + dados
plt.title("Top 10 Ranking de times")
plt.xlabel("Time")
plt.ylabel("Pontuação do time")
plt.xticks(rotation=45)              # gira os rótulos do eixo X (útil p/ nomes longos de time)
plt.tight_layout()                   # evita cortar texto nas bordas
plt.savefig(graficos_dir / "ranking_times.png")  # salva como imagem
plt.show()      


plt.figure(figsize=(10, 6))          # tamanho do gráfico
valores_resultados = df_consulta6.iloc[0].tolist()
plt.pie(valores_resultados, labels=['Vitórias em Casa', 'Vitórias como Visitante', 'Empates'], autopct='%1.1f%%')  # tipo de gráfico + dados
plt.title("Distribuição de Resultados")
plt.tight_layout()                   # evita cortar texto nas bordas
plt.savefig(graficos_dir / "distribuicao_resultados.png")  # salva como imagem
plt.show()      

plt.plot(
    df_consulta7["Mes"],  # Eixo X: Tempo/Datas
    df_consulta7["Media_Gols"],  # Eixo Y: Valores numéricos
    marker="o",  # Adiciona um ponto em cada nó do gráfico
    linestyle="-",  # Tipo de linha (contínua)
    color="b",  # Cor da linha (azul)
    linewidth=2,
)  # Espessura da linha

plt.title("Media de gols ao longo do tempo", fontsize=14)
plt.xlabel("Mês", fontsize=12)
plt.ylabel("Média de Gols", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.6)  # Adiciona linhas de grade ao fundo

# 7. Rotacionar as datas do eixo X para não sobrepor o texto
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig(graficos_dir / "media_gols_por_mes.png")
plt.show() 
