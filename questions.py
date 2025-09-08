import random

class Question:
    
    def __init__(self, main_topic, sub_topic, question_text, right_answer, wrong_answers):
        self.main_topic = main_topic
        self.sub_topic = sub_topic
        self.question_text = question_text
        self.right_answer = right_answer
        self.wrong_answers = wrong_answers

    def get_options(self):
        options = [self.right_answer] + self.wrong_answers
        random.shuffle(options)
        return options

    def is_correct(self, x):
        return x == self.right_answer
    
