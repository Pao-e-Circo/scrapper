from pypdf import PdfReader

# TODO connect into the database and see if the current month is already scrapped.
print('iniciando a raspagem do relatório de presenças do mês atual.')

path = "t.pdf" ## TODO get from environment variable

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