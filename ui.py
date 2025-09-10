import json
import random
from questions import Question
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

root = tk.Tk()
root.title("Trivia Game")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

menu_frame = tk.Frame(root)
menu_frame.pack(expand=True)

title_label = tk.Label(menu_frame, text="Trivia Los Canos", font=("Arial", 48, "bold"))
title_label.pack(pady=20)

tk.Label(menu_frame, text="Team A name:", font=("Arial", 24)).pack()
team_a_entry = tk.Entry(menu_frame, font=("Arial", 14), width=20)
team_a_entry.pack(pady=10)

tk.Label(menu_frame, text="Team B name:", font=("Arial", 24)).pack()
team_b_entry = tk.Entry(menu_frame, font=("Arial", 14), width=20)
team_b_entry.pack(pady=10)


question_label = tk.Label(
    root,
    text="",
    font=("Arial", 36),
    wraplength=root.winfo_screenwidth() - 400,  # fit most of the TV width
    justify="center",
    anchor="center"
)
question_label.pack_forget()

button_frame = tk.Frame(root)
button_frame.pack_forget()

topic_frame = tk.Frame(root)
topic_frame.pack_forget()

subtopic_frame = tk.Frame(root)
subtopic_frame.pack_forget()

with open("questions.json", "r", encoding="utf-8") as f:
    content = json.load(f)

list_of_questions = []
for element in content:
    question = Question(
        element["main_topic"],
        element["sub_topic"],
        element["question_text"],
        element["right_answer"],
        element["wrong_answers"]
    )
    list_of_questions.append(question)

# Game state
scores = {"Team A": 0, "Team B": 0}
current_team = "Team A"
remaining_questions = list_of_questions.copy()

answer_buttons = []
for i in range(4):
    btn = tk.Button(
        button_frame,
        text="",
        font=("Arial", 24),
        height=5,
        width=30,
        wraplength=(root.winfo_screenwidth() // 2) - 100,
        justify="center"
    )
    row = i // 2   # 0 or 1
    col = i % 2    # 0 or 1
    btn.grid(row=row, column=col, padx=40, pady=20, sticky="nsew")
    answer_buttons.append(btn)
for r in range(2):
    button_frame.grid_rowconfigure(r, weight=1)
for c in range(2):
    button_frame.grid_columnconfigure(c, weight=1)
    
# Label for scores
score_label = tk.Label(root, text=f"Team A: 0  |  Team B: 0", font=("Arial", 28))
score_label.pack_forget()

# Label for current team
team_label = tk.Label(root, text=f"Current team: {current_team}", font=("Arial", 28))
team_label.pack_forget()

button_images = {}  # keep references to prevent garbage collection

def load_button_image(path, size=(300, 150)):
    if not os.path.exists(path):
        return None
    img = Image.open(path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def start_game():
    
    team_a_name = team_a_entry.get().strip() or "Team A"
    team_b_name = team_b_entry.get().strip() or "Team B"

    # Reset scores dictionary with custom names
    scores = {team_a_name: 0, team_b_name: 0}
    current_team = team_a_name

    # Update labels
    score_label.config(text=f"{team_a_name}: 0  |  {team_b_name}: 0")
    team_label.config(text=f"Current team: {current_team}")

    # Hide menu, show game
    menu_frame.pack_forget()
    show_topics()

start_button = tk.Button(menu_frame, text="Start Game", font=("Arial", 28), width=15, height=2, command=start_game)
start_button.pack(pady=20)
def load_question():
    global current_question, remaining_questions

    if not remaining_questions:
        messagebox.showinfo("Game Over", f"Final scores:\nTeam A: {scores['Team A']}\nTeam B: {scores['Team B']}")
        root.quit()
        return

    # Pick a random question
    current_question = random.choice(remaining_questions)

    # Update question text
    question_label.config(text=current_question.question_text)

    # Shuffle options
    options = current_question.get_options()

    # Assign options to buttons
    for i, btn in enumerate(answer_buttons):
        btn.config(text=options[i], command=lambda opt=options[i]: check_answer(opt))

def check_answer(selected_answer):
    global current_team, remaining_questions

    # Disable all buttons to prevent multiple clicks
    for btn in answer_buttons:
        btn.config(state="disabled")

    # Turn buttons red/green
    for btn in answer_buttons:
        if btn.cget("text") == current_question.right_answer:
            btn.config(bg="green", fg="white")  # correct answer is green
        elif btn.cget("text") == selected_answer:
            btn.config(bg="red", fg="white")  # selected wrong answer is red
    
    # Update score if correct
    if current_question.is_correct(selected_answer):
        scores[current_team] += 1

    remaining_questions.remove(current_question)

    # Switch team
    current_team = "Team B" if current_team == "Team A" else "Team A"
    team_label.config(text=f"Current team: {current_team}")
    score_label.config(text=f"Team A: {scores['Team A']}  |  Team B: {scores['Team B']}")

    # Back to topic selection
    root.after(1500, lambda: reset_buttons_and_show_topics())

def reset_buttons_and_show_topics():
    # Reset button colors and enable them
    for btn in answer_buttons:
        btn.config(bg="gray90", fg="black", state="normal")

    # Hide question label and button frame
    question_label.pack_forget()
    button_frame.pack_forget()

    # Go back to topic selection
    show_topics()

def show_topics():
    topic_frame.pack(pady=20)
    team_label.pack(pady=20)
    score_label.pack(pady=20)
    subtopic_frame.pack_forget()
    question_label.pack_forget()
    button_frame.pack_forget()

    # Clear previous buttons
    for widget in topic_frame.winfo_children():
        widget.destroy()
    for widget in subtopic_frame.winfo_children():
        widget.destroy()

    # Get all topics that have at least one remaining question
    available_topics = sorted(set(q.main_topic for q in remaining_questions))

    tk.Label(topic_frame, text=f"{current_team}, choose a topic:", font=("Arial", 24)).pack(pady=5)

    for topic in available_topics:
        image_path = f"images/{topic}.jpg"  # Example: images/Science.jpg
        img = load_button_image(image_path)
        button_images[topic] = img  # keep reference

        if img:
            btn = tk.Button(
                topic_frame,
                text=topic,
                font=("Arial", 22, "bold"),
                image=img,
                compound="center",  # text overlays image
                width=300, height=150,
                command=lambda t=topic: show_subtopics(t)
            )
        else:
            btn = tk.Button(
                topic_frame,
                text=topic,
                font=("Arial", 22, "bold"),
                width=25, height=3,
                command=lambda t=topic: show_subtopics(t)
            )
        btn.pack(pady=10)


def show_subtopics(chosen_topic):
    topic_frame.pack_forget()
    subtopic_frame.pack(pady=20)

    # Clear previous subtopic buttons
    for widget in subtopic_frame.winfo_children():
        widget.destroy()

    # Get subtopics with remaining questions in this topic
    available_subtopics = sorted(set(
        q.sub_topic for q in remaining_questions if q.main_topic == chosen_topic
    ))

    tk.Label(subtopic_frame, text=f"{current_team}, choose a subtopic:", font=("Arial", 24)).pack(pady=5)

    for subtopic in available_subtopics:
        image_path = f"images/{chosen_topic}_{subtopic}.jpg"  # Example: images/Science_Physics.jpg
        img = load_button_image(image_path)
        button_images[f"{chosen_topic}_{subtopic}"] = img  # keep reference

        if img:
            btn = tk.Button(
                subtopic_frame,
                text=subtopic,
                font=("Arial", 22, "bold"),
                image=img,
                compound="center",
                width=300, height=150,
                command=lambda st=subtopic: start_question(chosen_topic, st)
            )
        else:
            btn = tk.Button(
                subtopic_frame,
                text=subtopic,
                font=("Arial", 22, "bold"),
                width=24, height=3,
                command=lambda st=subtopic: start_question(chosen_topic, st)
            )
        btn.pack(pady=10)

def start_question(topic, subtopic):
    subtopic_frame.pack_forget()
    question_label.pack(pady=40, expand=True, fill="both")
    button_frame.pack(pady=20)
    # Clear topic/subtopic buttons
    for widget in topic_frame.winfo_children():
        widget.destroy()
    for widget in subtopic_frame.winfo_children():
        widget.destroy()

    # Pick a random question in this topic/subtopic
    global current_question
    available_questions = [
        q for q in remaining_questions if q.main_topic == topic and q.sub_topic == subtopic
    ]
    if not available_questions:
        messagebox.showinfo("No questions", "No remaining questions in this subtopic.")
        show_topics()
        return

    current_question = random.choice(available_questions)

    # Display question text
    question_label.config(text=current_question.question_text)

    # Shuffle options and assign to buttons
    options = current_question.get_options()
    for i, btn in enumerate(answer_buttons):
        btn.config(text=options[i], command=lambda opt=options[i]: check_answer(opt))



root.mainloop()