import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class ClassroomEndpoint:
    def __init__(self, scopes):
        self.SCOPES = scopes
        self.creds = None
        self.course_json = []

    def authenticate(self):
        # Fazer a autenticação e criação do token
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
            # Para funcionar deve ser criado as credenciais no google cloud 
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def get_service(self):
        try:
            self.service = build("classroom", "v1", credentials=self.creds)
            return self.service
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def __clear_course_json(self):
        self.course_json = []

    def get_courses_informations_by_user(self):
        try:
            results = self.service.courses().list().execute()
            courses = results.get("courses", [])
            self.__clear_course_json()
            for course in courses:
                self.course_json.append({
                "course_id":         course.get("id"),
                "name":              course.get("name"),
                "section":           course.get("section"),
                "description":       course.get("description"),
                "room":              course.get("room"),
                "state":             course.get("courseState"),
                "enrollment_code":   course.get("enrollmentCode"),
                "creation_time":     course.get("creationTime"),
                "update_time":       course.get("updateTime"),
                "teacher_folder_id": course.get("teacherFolder", {}).get("id"),
            })
            return self.course_json
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def get_curser_informations_by_id(self, course_id):
        try:
            course = self.service.courses().get(id=course_id).execute()
            self.__clear_course_json()
            self.course_json.append({
                "course_id":         course["id"],
                "name":              course["name"],
                "section":           course["section"],
                "description":       course.get("description"),
                "room":              course["room"],
                "state":             course["courseState"],
                "enrollment_code":   course["enrollmentCode"],
                "creation_time":     course["creationTime"],
                "update_time":       course["updateTime"],
                "teacher_folder_id": course.get("teacherFolder", {}).get("id"),
            })
            return self.course_json
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
        
    def get_works_by_course_id(self, course_id):
        try:
            results = self.service.courses().courseWork().list(courseId=course_id).execute()
            works = results.get("courseWork", [])
            self.works_by_course_json = []
            for work in works:
                self.works_by_course_json.append({
                    'work_id': work.get("id"),
                    'title': work.get("title"),
                    'description': work.get("description"),
                    'state': work.get("state"),
                    'materials': work.get("materials", []), # lista de materias que o professor disponibiliza na atividade
                    'dueDate': work.get("dueDate"),
                    'maxPoints': work.get("maxPoints"), # Valor daquela atv vai de 0 a 100
                    'assigneeMode': work.get("assigneeMode"), # Pode ser ALL ou INDIVIDUAL
                })
            return self.works_by_course_json
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None