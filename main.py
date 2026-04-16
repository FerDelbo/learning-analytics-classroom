from src.endpoint import ClassroomEndpoint
import yaml

def load_ymal():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

config = load_ymal()
classroom = ClassroomEndpoint(config["SCOPES"])
classroom.authenticate()
service = classroom.get_service()

# courses_info = classroom.get_courses_informations_by_user()
# for course in courses_info:
#     print("====================================")
#     print(f"Course Name: {course['name']}")
#     print(f"Course ID: {course['course_id']}")
#     print(f"Section: {course['section']}")
#     print(f"Description: {course['description']}")
#     print(f"Room: {course['room']}")
#     print(f"State: {course['state']}")
#     print(f"Enrollment Code: {course['enrollment_code']}")
#     print(f"Creation Time: {course['creation_time']}")
#     print(f"Update Time: {course['update_time']}")
#     print(f"Teacher Folder ID: {course['teacher_folder_id']}")
#     print("====================================\n\n")

# data_science_course = classroom.get_curser_informations_by_id("818860440446")
# print(data_science_course)

