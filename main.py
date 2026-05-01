from src.endpoint import ClassroomEndpoint
import yaml

def load_ymal():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

def print_works_by_course(works):
    for work in works:
        print("====================================")
        print(f"Work Title: {work['title']}")
        print(f"Work ID: {work['work_id']}")
        print(f"Work Description: {work.get('description', 'No description')}")
        print(f"Work State: {work['state']}")
        print(f"Work Max Points: {work['maxPoints']}")
        print(f"Work Materials: {work['materials']}")
        print(f"Work Due Date: {work['dueDate']}")
        
        print(f"Work Assignee Mode: {work['assigneeMode']}")
        print("====================================\n\n")

def print_course_info(course):
    print("====================================")
    print(f"Course Name: {course['name']}")
    print(f"Course ID: {course['course_id']}")
    print(f"Section: {course['section']}")
    print(f"Description: {course['description']}")
    print(f"Room: {course['room']}")
    print(f"State: {course['state']}")
    print(f"Enrollment Code: {course['enrollment_code']}")
    print(f"Creation Time: {course['creation_time']}")
    print(f"Update Time: {course['update_time']}")
    print(f"Teacher Folder ID: {course['teacher_folder_id']}")
    print("====================================\n\n")


def main():
    config = load_ymal()
    classroom = ClassroomEndpoint(config["SCOPES"])
    classroom.authenticate()
    service = classroom.get_service()

    courses_info = classroom.get_courses_informations_by_user()
    print("Quandtidade de cursos: ", len(courses_info))
    print_course_info(courses_info[0])

    # Ciencia de dados 3B TDS: 818860440446
    data_science_course = classroom.get_curser_informations_by_id("818860440446")
    print(data_science_course)

    data_sceinte_course_works = classroom.get_works_by_course_id("818860440446")
    print_works_by_course(data_sceinte_course_works)
    # print(data_sceinte_course_works)

if __name__ == "__main__":
    main()