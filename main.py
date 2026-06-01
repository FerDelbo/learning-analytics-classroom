from src.endpoint import ClassroomEndpoint
import yaml

def load_yaml():
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config

def print_works_by_course(works):
    for work in works:
        print("====================================")
        print(f"Work Title: {work['title']}")
        print(f"Work ID: {work['work_id']}")
        print(f"Work Description: {work.get('description', 'No description')}")
        print(f"Work State: {work['state']}")
        print(f"Work Max Points: {work.get('maxPoints', 'N/A')}")
        print(f"Work Materials: {work.get('materials', [])}")
        print(f"Work Due Date: {work.get('dueDate', 'N/A')}")
        print(f"Work Assignee Mode: {work.get('assigneeMode', 'N/A')}")
        print("====================================\n\n")

def print_course_info(course):
    print("====================================")
    print(f"Course Name: {course['name']}")
    print(f"Course ID: {course['course_id']}")
    print(f"Section: {course.get('section', 'N/A')}")
    print(f"Description: {course.get('description', 'N/A')}")
    print(f"Room: {course.get('room', 'N/A')}")
    print(f"State: {course['state']}")
    print(f"Enrollment Code: {course.get('enrollment_code', 'N/A')}")
    print(f"Creation Time: {course['creation_time']}")
    print(f"Update Time: {course['update_time']}")
    print(f"Teacher Folder ID: {course.get('teacher_folder_id', 'N/A')}")
    print("====================================\n\n")

def print_people_by_course(title, people):
    print("====================================")
    print(title)
    for person in people:
        print(f"Name: {person['full_name']}")
        print(f"User ID: {person['user_id']}")
        print(f"Email: {person['email']}")
        print(f"Photo URL: {person.get('photo_url', 'N/A')}")
        print("------------------------------------")
    print("====================================\n\n")


config = load_yaml()
classroom = ClassroomEndpoint(config["SCOPES"])
classroom.authenticate()
classroom.get_service()

# ID da disciplina de Ciência de Dados 3B TDS
id_ciencia_dados = "818860440446"

print("=== Buscando informações gerais dos cursos ===")
courses_info = classroom.get_courses_informations_by_user()
print("Quantidade de cursos: ", len(courses_info))
if courses_info:
    print_course_info(courses_info[0])

print(f"\n=== Buscando Detalhes do Curso: {id_ciencia_dados} ===")
data_science_course = classroom.get_curser_informations_by_id(id_ciencia_dados)
if data_science_course:
    print_course_info(data_science_course[0])
    classroom.save_to_json(data_science_course, "data/ciencia_dados_info.json")

print("\n=== Buscando Atividades (CourseWorks) ===")
data_science_course_works = classroom.get_works_by_course_id(id_ciencia_dados)
print_works_by_course(data_science_course_works)
classroom.save_to_json(data_science_course_works, "data/ciencia_dados_atividades.json")

print("\n=== Buscando Estudantes ===")
students = classroom.get_students_by_course_id(id_ciencia_dados)
print_people_by_course("Students", students)
classroom.save_to_json(students, "data/ciencia_dados_estudantes.json")

print("\n=== Buscando Professores ===")
teachers = classroom.get_teachers_by_course_id(id_ciencia_dados)
print_people_by_course("Teachers", teachers)
classroom.save_to_json(teachers, "data/ciencia_dados_professores.json")
