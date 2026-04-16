# import os.path

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# # If modifying these scopes, delete the file token.json.
# # No seu arquivo Python, use estas duas URLs:
# SCOPES = [
#     "https://www.googleapis.com/auth/classroom.courses.readonly",
#     "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly"
#     # "https://www.googleapis.com/auth/classroom.coursework.students.readonly"
# ]

# def main():
#   """Shows basic usage of the Classroom API.
#   Prints the names of the courses where the user is a teacher and their coursework.
#   """
#   creds = None
#   # The file token.json stores the user's access and refresh tokens, and is
#   # created automatically when the authorization flow completes for the first
#   # time.
#   if os.path.exists("token.json"):
#     creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#   # If there are no (valid) credentials available, let the user log in.
#   if not creds or not creds.valid:
#     if creds and creds.expired and creds.refresh_token:
#       creds.refresh(Request())
#     else:
#       flow = InstalledAppFlow.from_client_secrets_file(
#           "credentials.json", SCOPES
#       )
#       creds = flow.run_local_server(port=0)
#     # Save the credentials for the next run
#     with open("token.json", "w") as token:
#       token.write(creds.to_json())

#   try:
#     service = build("classroom", "v1", credentials=creds)

#     # Call the Classroom API to list courses where user is teacher
#     results = service.courses().list().execute()
#     courses = results.get("courses", [])

#     # if not courses:
#     #   print("No courses found where you are a teacher.")
#     #   return
#     # # Prints the names of the courses and their coursework.
#     # print("Courses where you are a teacher:")
#     for course in courses:
#       print(f"\nCourse: {course['name']} (ID: {course['id']})")
#       coursework_results = service.courses().courseWork().list(courseId=course['id']).execute()
#       coursework = coursework_results.get("courseWork", [])
      
#     # #   if not coursework:
#     # #     print("  No coursework found.")
#     # #   else:
#     # #     print("  Coursework:")
#       for work in coursework:
#         print(f"    - {work['title']} (ID: {work['id']}, Course ID: {course['id']})")

#   except HttpError as error:
#     print(f"An error occurred: {error}")


# if __name__ == "__main__":
#   main()

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopos necessários: Cursos, Trabalhos de Alunos e Perfis/Rosters
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.students.readonly",
    "https://www.googleapis.com/auth/classroom.rosters.readonly"
]

def main():
    creds = None
    # IMPORTANTE: Se o erro de escopo persistir, delete o token.json antes de rodar
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("classroom", "v1", credentials=creds)

        # Cache de nomes para evitar milhares de requisições repetidas
        cache_alunos = {}

        results = service.courses().list().execute()
        courses = results.get("courses", [])

        for course in courses:
            print("\n" + "="*80)
            print(f"TURMA: {course['name']}")
            
            coursework_results = service.courses().courseWork().list(courseId=course['id']).execute()
            coursework_list = coursework_results.get("courseWork", [])
            
            for work in coursework_list:
                # Valor total da atividade
                valor_atividade = work.get('maxPoints', 'N/A')
                print(f"\n  > Atividade: {work['title']} (Vale: {valor_atividade})")
                
                submissions_results = service.courses().courseWork().studentSubmissions().list(
                    courseId=course['id'], 
                    courseWorkId=work['id']
                ).execute()
                
                submissions = submissions_results.get("studentSubmissions", [])
                
                if not submissions:
                    print("    - Nenhuma entrega.")
                else:
                    for sub in submissions:
                        user_id = sub.get('userId')    
                        # Busca o nome no cache ou na API
                        if user_id not in cache_alunos:
                            try:
                                profile = service.userProfiles().get(userId=user_id).execute()
                                cache_alunos[user_id] = profile.get('name', {}).get('fullName', 'N/A')
                            except:
                                cache_alunos[user_id] = f"ID: {user_id}"

                        nome = cache_alunos[user_id]
                        nota = sub.get('assignedGrade', 'Pendente')
                        status = sub.get('state')
                        atrasado = "SIM" if sub.get('late') else "NÃO"
                        
                        # Tempo realizado (Data da última atualização da entrega)
                        tempo_realizado = sub.get('updateTime', 'N/A')
                        
                        print(f"    - {nome[:20]:<20} | Nota: {nota}/{valor_atividade} | Atraso: {atrasado} | Entrega: {tempo_realizado}")

    except HttpError as error:
        print(f"Ocorreu um erro na API: {error}")

if __name__ == "__main__":
    main()