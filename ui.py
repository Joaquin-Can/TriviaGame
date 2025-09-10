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

# Clear any previous buttons in button_frame
for widget in button_frame.winfo_children():
    widget.destroy()

answer_buttons = []

# Create 4 buttons in 2x2 grid
for i in range(4):
    btn = tk.Button(
        button_frame,
        text="",
        font=("Arial", 24),
        wraplength=(root.winfo_screenwidth() // 2) - 100,
        justify="center",
        height=5
    )
    row = i // 2  # 0 or 1
    col = i % 2   # 0 or 1
    btn.grid(row=row, column=col, sticky="nsew", padx=20, pady=20)
    answer_buttons.append(btn)

# Make rows and columns expand equally
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

def load_button_image(path, target_width, target_height):
    try:
        img = Image.open(path)
        img = img.resize((target_width, target_height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return None

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
    topic_frame.pack(pady=20, expand=True, fill="both")
    team_label.pack(pady=20)
    score_label.pack(pady=20)
    subtopic_frame.pack_forget()
    question_label.pack_forget()
    button_frame.pack_forget()

    # Clear previous buttons
    for widget in topic_frame.winfo_children():
        widget.destroy()

    available_topics = sorted(set(q.main_topic for q in remaining_questions))

    tk.Label(topic_frame, text=f"{current_team}, choose a topic:", font=("Arial", 28)).grid(row=0, column=0, columnspan=3, pady=20)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    button_width = (screen_width - 120) // 3  # 3 per row
    button_height = int(screen_height * 0.25)

    for i, topic in enumerate(available_topics):
        image_path = f"images/{topic}.jpg"
        img = load_button_image(image_path, button_width, button_height)
        button_images[topic] = img  # keep reference

        btn = tk.Button(
            topic_frame,
            text=topic,
            font=("Arial", 22, "bold"),
            image=img,
            compound="center",
            command=lambda t=topic: show_subtopics(t)
        )

        row = i // 3 + 1
        col = i % 3

        # Center last row if only 2 buttons
        if row == (len(available_topics) - 1) // 3 + 1 and len(available_topics) % 3 == 2 and i >= len(available_topics) - 2:
            if col == 0:
                col = 0
            elif col == 1:
                col = 2

        btn.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

    for c in range(3):
        topic_frame.grid_columnconfigure(c, weight=1)


def show_subtopics(chosen_topic):
    topic_frame.pack_forget()
    subtopic_frame.pack(pady=20, expand=True, fill="both")

    # Clear previous subtopic buttons
    for widget in subtopic_frame.winfo_children():
        widget.destroy()

    available_subtopics = sorted(set(
        q.sub_topic for q in remaining_questions if q.main_topic == chosen_topic
    ))

    tk.Label(subtopic_frame, text=f"{current_team}, choose a subtopic:", font=("Arial", 28)).grid(row=0, column=0, columnspan=2, pady=20)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    button_width = (screen_width - 80) // 2  # 2 per row
    button_height = int(screen_height * 0.25)

    for i, subtopic in enumerate(available_subtopics):
        image_path = f"images/{chosen_topic}_{subtopic}.jpg"
        img = load_button_image(image_path, button_width, button_height)
        button_images[f"{chosen_topic}_{subtopic}"] = img

        btn = tk.Button(
            subtopic_frame,
            text=subtopic,
            font=("Arial", 22, "bold"),
            image=img,
            compound="center",
            command=lambda st=subtopic: start_question(chosen_topic, st)
        )

        row = i // 2 + 1
        col = i % 2

        # Center last row if only 1 button
        if row == (len(available_subtopics) - 1) // 2 + 1 and len(available_subtopics) % 2 == 1 and i == len(available_subtopics) - 1:
            col = 0
            btn.grid(row=row, column=col, columnspan=2, padx=20, pady=20, sticky="nsew")
        else:
            btn.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

    for c in range(2):
        subtopic_frame.grid_columnconfigure(c, weight=1)

def start_question(topic, subtopic):
    # Hide other frames
    topic_frame.pack_forget()
    subtopic_frame.pack_forget()

    # Show question and buttons
    question_label.pack(pady=40, expand=True, fill="both")
    button_frame.pack(pady=20, expand=True, fill="both")  # <-- important

    # Pick a random question
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

    # Shuffle options
    options = current_question.get_options()

    # Assign options to buttons
    for i, btn in enumerate(answer_buttons):
        btn.config(
            text=options[i],
            command=lambda opt=options[i]: check_answer(opt),
            bg="lightgray",  # reset button color
            fg="black",
            state="normal"
        )


root.mainloop()