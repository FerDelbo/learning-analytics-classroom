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

    def get_students_by_course_id(self, course_id):
        try:
            students_by_course_json = []
            request = self.service.courses().students().list(courseId=course_id)

            while request is not None:
                results = request.execute()
                students = results.get("students", [])

                for student in students:
                    profile = student.get("profile", {})
                    students_by_course_json.append({
                        "course_id": course_id,
                        "user_id": student.get("userId"),
                        "full_name": profile.get("name", {}).get("fullName"),
                        "email": profile.get("emailAddress"),
                        "photo_url": profile.get("photoUrl"),
                    })

                request = self.service.courses().students().list_next(request, results)

            return students_by_course_json
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def get_teachers_by_course_id(self, course_id):
        try:
            teachers_by_course_json = []
            request = self.service.courses().teachers().list(courseId=course_id)

            while request is not None:
                results = request.execute()
                teachers = results.get("teachers", [])

                for teacher in teachers:
                    profile = teacher.get("profile", {})
                    teachers_by_course_json.append({
                        "course_id": course_id,
                        "user_id": teacher.get("userId"),
                        "full_name": profile.get("name", {}).get("fullName"),
                        "email": profile.get("emailAddress"),
                        "photo_url": profile.get("photoUrl"),
                    })

                request = self.service.courses().teachers().list_next(request, results)

            return teachers_by_course_json
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def get_quiz_questions(self, course_id: str) -> list:
        try:
            results = self.service.courses().courseWork().list(courseId=course_id).execute()
            works   = results.get("courseWork", [])

            result = []
            for w in works:
                due     = w.get("dueDate")
                due_str = f"{due['year']}-{due['month']:02d}-{due['day']:02d}" if due else None

                choices = None
                if w.get("workType") == "MULTIPLE_CHOICE_QUESTION":
                    choices = w.get("multipleChoiceQuestion", {}).get("choices", [])

                result.append({
                    "work_id":      w.get("id"),
                    "course_id":    course_id,
                    "title":        w.get("title"),
                    "description":  w.get("description"),
                    "work_type":    w.get("workType"),
                    "max_points":   w.get("maxPoints"),
                    "due_date":     due_str,
                    "state":        w.get("state"),
                    "choices":      choices,
                    "creation_time": w.get("creationTime"),
                    "update_time":   w.get("updateTime"),
                })

            return result
        except HttpError as error:
            print(f"[ERRO] get_quiz_questions (curso {course_id}): {error}")
            return []


    def get_course_grades(self, course_id):
        works = self.get_quiz_questions(course_id)
        result = []

        for work in works:
            try:
                subs_result = self.service.courses().courseWork().studentSubmissions().list(
                    courseId=course_id,
                    courseWorkId=work["work_id"],
                ).execute()

                for sub in subs_result.get("studentSubmissions", []):
                    user_id = sub.get("userId")
                    profile = self._get_student_profile(user_id)
                    state   = sub.get("state")

                    answer = None
                    if "multipleChoiceSubmission" in sub:
                        answer = sub["multipleChoiceSubmission"].get("answer")
                    elif "shortAnswerSubmission" in sub:
                        answer = sub["shortAnswerSubmission"].get("answer")

                    creation_time = sub.get("creationTime")
                    update_time   = sub.get("updateTime")
                    duration      = self.__calc_duration(creation_time, update_time)

                    completed = state in ("TURNED_IN", "RETURNED")

                    result.append({
                        "course_id":      course_id,
                        "work_id":        work["work_id"],
                        "work_title":     work["title"],
                        "max_points":     work["max_points"],
                        "user_id":        user_id,
                        "full_name":      profile["full_name"],
                        "email":          profile["email"],
                        "assigned_grade": sub.get("assignedGrade"),
                        "draft_grade":    sub.get("draftGrade"),
                        "state":          state,
                        "completed":      completed,
                        "late":           sub.get("late", False),
                        "answer":         answer,
                        "update_time":    sub.get("updateTime"),
                        "duration":       duration,
                    })

            except HttpError as error:
                print(f"[ERRO] get_course_grades - atividade {work['work_id']}: {error}")

        return result

    def get_activities_by_user(self, course_id):
        grades = self.get_course_grades(course_id)
        users  = {}

        for entry in grades:
            uid = entry["user_id"]
            if uid not in users:
                users[uid] = {
                    "user_id":    uid,
                    "full_name":  entry["full_name"],
                    "email":      entry["email"],
                    "activities": [],
                }
            users[uid]["activities"].append({
                "work_id":        entry["work_id"],
                "work_title":     entry["work_title"],
                "max_points":     entry["max_points"],
                "assigned_grade": entry["assigned_grade"],
                "state":          entry["state"],
                "completed":      entry["completed"],
                "late":           entry["late"],
                "answer":         entry["answer"],
                "update_time":    entry["update_time"],
                "duration":       entry["duration"],
            })

        return list(users.values())