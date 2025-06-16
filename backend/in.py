import sqlite3

conn = sqlite3.connect('eduplataforma.db')  # Caminho completo, se necessário
cursor = conn.cursor()

# Exemplo: listar escolas
cursor.execute("SELECT * FROM escola")
for row in cursor.fetchall():
    print(row)

conn.close()