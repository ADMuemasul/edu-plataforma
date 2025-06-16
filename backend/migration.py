from app import app, db
from database import Questao
from sqlalchemy import text

def add_componente_column():
    # Adicionar o campo componente na tabela questao
    with app.app_context():
        connection = db.engine.connect()
        try:
            print("Adicionando coluna componente na tabela questao...")
            if db.engine.url.drivername == 'sqlite':
                connection.execute(text("ALTER TABLE questao ADD COLUMN componente VARCHAR(50)"))
            else:
                connection.execute(text("ALTER TABLE questao ADD COLUMN componente VARCHAR(50) NULL"))
            connection.commit()
            print("Coluna adicionada com sucesso!")
        except Exception as e:
            # Se a coluna já existir, simplesmente ignoramos o erro
            print(f"Erro ao adicionar coluna (pode ser que ela já exista): {e}")
        finally:
            connection.close()

if __name__ == '__main__':
    add_componente_column() 