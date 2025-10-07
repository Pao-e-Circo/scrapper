from pypdf import PdfReader
import psycopg2

def connect_database():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="paoecirco.org",
            user="postgres",
            password="postgres",
            port="5432" # Default is 5432
        )
        print("Conexão com o PostgreSQL bem-sucedida.")

    except psycopg2.Error as e:
        print(f"Erro ao se conectar ao PostgreSQL: {e}")

# TODO connect into the database and see if the current month is already scrapped.
print('Iniciando a raspagem do relatório de presenças do mês atual.')

path = "t.pdf" ## TODO get from environment variable

connect_database()

reader = PdfReader(path)
page = reader.pages[0]
text = page.extract_text().splitlines()

current_line = 5

session_type = text[current_line] ## extraordinária, ordinária

current_line += 2

session_date = text[current_line]
current_line += 1

print(session_type)
print(session_date)

votes = []

for i in text[current_line:]:
    if not any(x in i for x in ['PRESENTE', 'Ausente', 'Justificado']):
        continue
    votes.append(i)

for i in votes:
    print(i)