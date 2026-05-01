import json

def salvar_json(nome: str, dados) -> None:
    with open(f"{nome}.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"  💾 Salvo: {nome}.json ({len(dados)} registros)")


def main():
    api = ClassroomEndpoint(config["SCOPES"])
    api.authenticate()
    print("✅ Autenticado!\n")

    # 1. Lista todos os cursos
    print("=" * 50)
    print("1. get_courses_informations_by_user")
    print("=" * 50)
    cursos = api.get_courses_informations_by_user()
    for i, c in enumerate(cursos):
        print(f"  [{i}] {c['name']} — ID: {c['course_id']}")
    salvar_json("cursos", cursos)

    if not cursos:
        print("Nenhum curso encontrado. Encerrando.")
        return

    # Usa o terceiro curso para testar os demais endpoints
    course_id   = cursos[13]["course_id"]
    course_name = cursos[13]["name"]
    print(f"\n🎯 Testando com o curso: {course_name} ({course_id})\n")

    # 2. Curso por ID
    print("=" * 50)
    print("2. get_course_informations_by_id")
    print("=" * 50)
    curso = api.get_course_informations_by_id(course_id)
    print(f"  Nome: {curso.get('name')}")
    print(f"  Seção: {curso.get('section')}")
    print(f"  Estado: {curso.get('state')}")

    # 3. Alunos
    print("\n" + "=" * 50)
    print("3. get_students_informations")
    print("=" * 50)
    alunos = api.get_students_informations(course_id)
    for a in alunos:
        print(f"  {a['full_name']} — {a['email']}")
    salvar_json("alunos", alunos)

    # 4. Papéis
    print("\n" + "=" * 50)
    print("4. get_users_roles")
    print("=" * 50)
    roles = api.get_users_roles(course_id)
    for r in roles:
        print(f"  [{r['role'].upper()}] {r['full_name']} — {r['email']}")
    salvar_json("roles", roles)

    # 5. Atividades
    print("\n" + "=" * 50)
    print("5. get_quiz_questions")
    print("=" * 50)
    atividades = api.get_quiz_questions(course_id)
    for a in atividades:
        print(f"  {a['title']} | Tipo: {a['work_type']} | Pontos: {a['max_points']}")
        if a["choices"]:
            print(f"    Opções: {a['choices']}")
    salvar_json("atividades", atividades)

    # 6. Notas
    print("\n" + "=" * 50)
    print("6. get_course_grades")
    print("=" * 50)
    notas = api.get_course_grades(course_id)
    for n in notas:
        print(f"  {n['full_name']} | {n['work_title']} | Nota: {n['assigned_grade']}/{n['max_points']} | Atraso: {n['late']}")
    salvar_json("notas", notas)

    # 7. Atividades por aluno
    print("\n" + "=" * 50)
    print("7. get_activities_by_user")
    print("=" * 50)
    por_aluno = api.get_activities_by_user(course_id)
    for u in por_aluno:
        print(f"\n  👤 {u['full_name']} ({len(u['activities'])} atividade(s))")
        for atv in u["activities"]:
            print(f"     - {atv['work_title']} | Nota: {atv['assigned_grade']} | Estado: {atv['state']}")
    salvar_json("por_aluno", por_aluno)

    print("\n✅ Todos os endpoints testados com sucesso!")
