import os
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class ClassroomEndpoint:
    def __init__(self, scopes):
        self.creds   = None
        self.service = None
        self._student_cache = {}  # Evita requisições repetidas de perfil
        self.SCOPES = scopes

    # ─────────────────────────────────────────────
    # AUTENTICAÇÃO
    # ─────────────────────────────────────────────

    def authenticate(self):
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        self.service = build("classroom", "v1", credentials=self.creds)

    # ─────────────────────────────────────────────
    # HELPER INTERNO
    # ─────────────────────────────────────────────

    def _get_student_profile(self, user_id: str) -> dict:
        """Busca nome e email de um aluno, com cache para evitar requisições repetidas."""
        if user_id not in self._student_cache:
            try:
                profile = self.service.userProfiles().get(userId=user_id).execute()
                self._student_cache[user_id] = {
                    "full_name": profile.get("name", {}).get("fullName"),
                    "email":     profile.get("emailAddress"),
                    "photo_url": profile.get("photoUrl"),
                }
            except HttpError:
                self._student_cache[user_id] = {
                    "full_name": None,
                    "email":     None,
                    "photo_url": None,
                }
        return self._student_cache[user_id]

    def _calc_duration(self, creation_time: str, update_time: str) -> dict | None:
        """
        Calcula o tempo entre o primeiro acesso (creationTime) e a última
        modificação (updateTime) de uma submissão.
        Retorna None se algum dos campos estiver ausente (ex: state = NEW).
        """
        if not creation_time or not update_time:
            return None
        try:
            fmt    = "%Y-%m-%dT%H:%M:%S.%fZ"
            start  = datetime.strptime(creation_time, fmt).replace(tzinfo=timezone.utc)
            end    = datetime.strptime(update_time,   fmt).replace(tzinfo=timezone.utc)
            delta  = end - start
            total  = int(delta.total_seconds())
            if total < 0:
                return None
            return {
                "seconds": total,
                "minutes": round(total / 60, 1),
                "formatted": f"{total // 3600:02d}h {(total % 3600) // 60:02d}m {total % 60:02d}s",
            }
        except ValueError:
            return None

    # ─────────────────────────────────────────────
    # ENDPOINT 1 — Cursos do usuário
    # Equivalente: local_myplugin_get_courses_informations_by_user
    # ─────────────────────────────────────────────

    def get_courses_informations_by_user(self) -> list:
        try:
            results = self.service.courses().list().execute()
            courses = results.get("courses", [])

            return [
                {
                    "course_id":       course.get("id"),
                    "name":            course.get("name"),
                    "section":         course.get("section"),
                    "description":     course.get("description"),
                    "room":            course.get("room"),
                    "state":           course.get("courseState"),
                    "enrollment_code": course.get("enrollmentCode"),
                    "creation_time":   course.get("creationTime"),
                    "update_time":     course.get("updateTime"),
                    "teacher_folder_id": course.get("teacherFolder", {}).get("id"),
                }
                for course in courses
            ]
        except HttpError as error:
            print(f"[ERRO] get_courses_informations_by_user: {error}")
            return []

    # ─────────────────────────────────────────────
    # ENDPOINT 2 — Curso por ID
    # Equivalente: local_myplugin_get_courses_informations_by_user (filtrado)
    # ─────────────────────────────────────────────

    def get_course_informations_by_id(self, course_id: str) -> dict:
        try:
            course = self.service.courses().get(id=course_id).execute()
            return {
                "course_id":       course.get("id"),
                "name":            course.get("name"),
                "section":         course.get("section"),
                "description":     course.get("description"),
                "room":            course.get("room"),
                "state":           course.get("courseState"),
                "enrollment_code": course.get("enrollmentCode"),
                "creation_time":   course.get("creationTime"),
                "update_time":     course.get("updateTime"),
                "teacher_folder_id": course.get("teacherFolder", {}).get("id"),
            }
        except HttpError as error:
            print(f"[ERRO] get_course_informations_by_id: {error}")
            return {}

    # ─────────────────────────────────────────────
    # ENDPOINT 3 — Informações dos alunos
    # Equivalente: local_myplugin_get_students_informations
    # ─────────────────────────────────────────────

    def get_students_informations(self, course_id: str) -> list:
        try:
            results  = self.service.courses().students().list(courseId=course_id).execute()
            students = results.get("students", [])

            return [
                {
                    "user_id":   s.get("userId"),
                    "full_name": s.get("profile", {}).get("name", {}).get("fullName"),
                    "email":     s.get("profile", {}).get("emailAddress"),
                    "photo_url": s.get("profile", {}).get("photoUrl"),
                    "course_id": course_id,
                }
                for s in students
            ]
        except HttpError as error:
            print(f"[ERRO] get_students_informations (curso {course_id}): {error}")
            return []

    # ─────────────────────────────────────────────
    # ENDPOINT 4 — Papéis dos usuários (professor/aluno)
    # Equivalente: local_myplugin_get_users_roles
    # ─────────────────────────────────────────────

    def get_users_roles(self, course_id: str) -> list:
        result = []

        try:
            teachers = self.service.courses().teachers().list(courseId=course_id).execute()
            for t in teachers.get("teachers", []):
                result.append({
                    "user_id":   t.get("userId"),
                    "full_name": t.get("profile", {}).get("name", {}).get("fullName"),
                    "email":     t.get("profile", {}).get("emailAddress"),
                    "role":      "teacher",
                    "course_id": course_id,
                })
        except HttpError as error:
            print(f"[ERRO] get_users_roles - teachers (curso {course_id}): {error}")

        try:
            students = self.service.courses().students().list(courseId=course_id).execute()
            for s in students.get("students", []):
                result.append({
                    "user_id":   s.get("userId"),
                    "full_name": s.get("profile", {}).get("name", {}).get("fullName"),
                    "email":     s.get("profile", {}).get("emailAddress"),
                    "role":      "student",
                    "course_id": course_id,
                })
        except HttpError as error:
            print(f"[ERRO] get_users_roles - students (curso {course_id}): {error}")

        return result

    # ─────────────────────────────────────────────
    # ENDPOINT 5 — Atividades e questões do curso
    # Equivalente: local_myplugin_get_quiz_questions
    # ─────────────────────────────────────────────

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

    # ─────────────────────────────────────────────
    # ENDPOINT 6 — Notas dos alunos
    # Equivalente: local_myplugin_core_grades_get_course_grades
    # ─────────────────────────────────────────────

    def get_course_grades(self, course_id: str) -> list:
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

                    answer = None
                    if "multipleChoiceSubmission" in sub:
                        answer = sub["multipleChoiceSubmission"].get("answer")
                    elif "shortAnswerSubmission" in sub:
                        answer = sub["shortAnswerSubmission"].get("answer")

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
                        "state":          sub.get("state"),
                        "late":           sub.get("late", False),
                        "answer":         answer,
                        "update_time":    sub.get("updateTime"),
                    })

            except HttpError as error:
                print(f"[ERRO] get_course_grades - atividade {work['work_id']}: {error}")

        return result

    # ─────────────────────────────────────────────
    # ENDPOINT 7 — Atividades agrupadas por aluno
    # Equivalente: local_myplugin_get_activities_by_user
    # ─────────────────────────────────────────────

    def get_activities_by_user(self, course_id: str) -> list:
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
                "late":           entry["late"],
                "answer":         entry["answer"],
                "update_time":    entry["update_time"],
            })

        return list(users.values())