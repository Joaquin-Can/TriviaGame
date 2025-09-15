import json 
from questions import Question
import random

with open("questions.json", "r", encoding="utf-8") as f:
    content = json.load(f)
    list_of_questions = []
    for element in content:
        question = Question(element["main_topic"], element["sub_topic"], element["question_text"], element["right_answer"], element["wrong_answers"])
        list_of_questions.append(question)

scores = {"Equipo A": 0, "Equipo B": 0}
current_team = "Equipo A"
remaining_questions = list_of_questions.copy()

topics = {
    "Ciencia": ["Física", "Biología", "Química", "Matemáticas", "Astronomía"],
    "Geografía": ["Capitales", "Paises/Continentes", "Biomas", "Fenómenos Climáticos", "Población"],
    "Arte": ["Pinturas", "Esculturas", "Música", "Literatura", "Danza"]
}

while remaining_questions:

    available_topics = set(q.main_topic for q in remaining_questions)

    print("Temas disponibles:")
    for t in available_topics:
        print("-", t)
    chosen_topic = input("Elije un tema: ").strip()

    available_subtopics = set(
        q.sub_topic for q in remaining_questions
        if q.main_topic == chosen_topic
    )
    print("Subtemas disponibles:")
    for st in available_subtopics:
        print("-", st)
    chosen_sub_topic = input("Elije un subtema: ").strip()

    available_questions = [
        q for q in remaining_questions
        if q.main_topic == chosen_topic and q.sub_topic == chosen_sub_topic
    ]

    question = random.choice(available_questions)

    options = question.get_options()
    print(question.question_text)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    try:
        choice = int(input("Selecciona tu respuesta: "))
        if choice < 1 or choice > 4:
            raise ValueError
    except ValueError:
        print("Respuesta inválida.")
        current_team = "Team B" if current_team == "Team A" else "Team A"
        continue
    
    selected_answer = options[choice - 1]
    
    if question.is_correct(selected_answer):
        print("¡Correcto!")
        scores[current_team] += 1
    else:
        print("¡Incorrecto!")
    
    remaining_questions.remove(question)

    current_team = "Team B" if current_team == "Team A" else "Team A"

    if scores["Team A"] == 2 or scores["Team B"] == 2:
        print("¡Final de juego!\n")
        break



