# Learning Analytics - Google Classroom Extractor

Este projeto é uma ferramenta de extração de dados automatizada que se conecta à API do **Google Classroom**. O objetivo é coletar informações detalhadas de turmas, alunos, professores e atividades, salvando tudo em arquivos estruturados (`.json`). 

## Funcionalidades

O script se autentica na sua conta Google e extrai automaticamente:
* **Informações dos Cursos:** Nome, sala, status e datas de criação.
* **Atividades (CourseWorks):** Título, descrição, nota máxima, tipo e datas de entrega.
* **Alunos (Roster):** Nome, e-mail e ID de usuário.
* **Professores:** Informações de contato e identificação.
* **Persistência de Dados:** Salva todos os retornos organizados na pasta `data/` no formato JSON.

---

## Endpoints da API Consumidos

O projeto utiliza a biblioteca cliente do Google (`googleapiclient`) para interagir com os seguintes endpoints REST da API do Google Classroom:

* **`courses.list`** (via `get_courses_informations_by_user`): 
  Lista todas as turmas em que o usuário autenticado está inscrito ou atua como professor. Útil para descobrir os IDs dos cursos.
* **`courses.get`** (via `get_curser_informations_by_id`): 
  Retorna os metadados detalhados de uma turma específica utilizando o seu ID (nome, seção, sala e datas de criação/atualização).
* **`courses.courseWork.list`** (via `get_works_by_course_id`): 
  Coleta todas as atividades, tarefas, perguntas e materiais postados no mural de uma disciplina específica. Traz dados como prazo de entrega (`dueDate`) e nota máxima.
* **`courses.students.list`** (via `get_students_by_course_id`): 
  Extrai a relação de todos os alunos matriculados na turma, incluindo dados de perfil como nome completo, e-mail e ID do usuário.
* **`courses.teachers.list`** (via `get_teachers_by_course_id`): 
  Retorna a lista de professores e auxiliares associados à disciplina.
* **`courses.courseWork.studentSubmissions.list`** (via `get_course_grades`): 
  Busca as submissões individuais dos alunos para cada atividade. É através deste endpoint que capturamos as notas, atrasos (`late`), status da entrega e respostas de múltipla escolha.

---

## Estrutura do Projeto

```text
learning-analytics-classroom/
│
├── data/                      # Onde os arquivos JSON serão salvos automaticamente
├── src/
│   ├── __init__.py
│   └── endpoint.py            # Classe principal de conexão com a API do Google
│
├── config.yaml                # Arquivo com os escopos de permissão da API
├── credentials.json           # [CRIADO PELO USUÁRIO] Credenciais do Google Cloud
├── token.json                 # Gerado automaticamente na 1ª execução
├── main.py                    # Script principal de execução
├── requirements.txt           # Dependências do projeto
└── README.md
```
## Pré-requisitos

Uma conta Google (institucional ou pessoal) com acesso a turmas no Classroom.

Um projeto configurado no Google Cloud Console para obter o arquivo de credenciais.

### Credenciais

A API do Google Classroom exige autenticação via OAuth2. Para que o script funcione, você precisa gerar um arquivo credentials.json:

1. Acesse o Google Cloud Console.

2. Crie um novo projeto (ex: "Learning Analytics App").

3. No menu lateral, vá em APIs e Serviços > Biblioteca.

4. Pesquise por Google Classroom API e clique em Ativar.

5. Vá em APIs e Serviços > Tela de consentimento OAuth:

  * Escolha o tipo de usuário (Externo ou Interno, dependendo da sua conta).
  
  * Preencha os campos obrigatórios (Nome do app, e-mail de suporte).
  
  * Na etapa de Escopos, não precisa adicionar nada (o script fará isso).
  
  * Adicione seu próprio e-mail como Usuário de Teste.

6. Vá em APIs e Serviços > Credenciais:

  * Clique em Criar Credenciais > ID do cliente OAuth.
  
  * Tipo de aplicativo: App para computador (Desktop app).
  
  * Clique em Criar.

7. Faça o download do arquivo JSON gerado, renomeie-o para credentials.json e coloque-o na raiz deste projeto.

