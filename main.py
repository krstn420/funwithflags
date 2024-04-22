import tkinter as tk
from tkinter import messagebox
import requests
import random
from PIL import Image, ImageTk
import io

class FlagGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flag Game")
        self.geometry("400x400")

        self.countries = self.fetch_countries()
        if not self.countries:  # If fetching countries failed
            return

        self.score = 0
        self.question_count = 0
        self.max_questions = 100
        self.incorrect_countries = []  # Track incorrect guesses

        # Cooldown to control reintroduction of incorrect answers
        self.cooldown = 3
        self.current_cooldown = 0  # Track current cooldown status

        self.flag_label = tk.Label(self)
        self.flag_label.pack(pady=20)

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack()

        self.buttons = []
        for i in range(3):
            button = tk.Button(
                self.buttons_frame,
                command=lambda idx=i: self.check_answer(idx),
            )
            button.grid(row=0, column=i, padx=10)
            self.buttons.append(button)

        self.score_label = tk.Label(self, text=f"Score: {self.score}")
        self.score_label.pack(pady=10)

        self.correct_answer = None
        self.next_question()

    def fetch_countries(self):
        try:
            response = requests.get("https://restcountries.com/v3.1/all")
            response.raise_for_status()  # Check for HTTP errors
            return response.json()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch country data: {e}")
            return None

    def select_question(self):
        if self.current_cooldown > 0:
            # If cooldown is active, pick a random country from the full list
            self.current_cooldown -= 1  # Decrease cooldown
            return random.choice(self.countries)
        elif self.incorrect_countries:
            # If no cooldown, reintroduce an incorrect question
            self.current_cooldown = self.cooldown  # Reset cooldown
            return self.incorrect_countries.pop(0)  # Remove the first one
        else:
            # If no cooldown and no incorrect answers, pick a random country
            return random.choice(self.countries)

    def next_question(self):
        if self.question_count >= self.max_questions:
            self.end_game()
            return

        self.question_count += 1
        correct_country = self.select_question()  # Pick the next question

        self.correct_answer = correct_country["name"]["common"]
        print(self.correct_answer)

        # Create the options with the correct answer and two incorrect answers
        possible_incorrect = [c for c in self.countries if c != correct_country]
        incorrect_countries = random.sample(possible_incorrect, 2)
        self.options = [self.correct_answer, incorrect_countries[0]["name"]["common"], incorrect_countries[1]["name"]["common"]]
        random.shuffle(self.options)

        # Update the flag image
        flag_url = correct_country["flags"]["png"]
        flag_response = requests.get(flag_url)
        flag_response.raise_for_status()  # Ensure successful request

        flag_image = Image.open(io.BytesIO(flag_response.content)).resize((150, 100))
        self.flag_tk_image = ImageTk.PhotoImage(flag_image)
        self.flag_label.configure(image=self.flag_tk_image)

        # Update the button labels with the shuffled options
        for button, option in zip(self.buttons, self.options):
            button.configure(text=option)

    def check_answer(self, option_index):
        if self.options[option_index] == self.correct_answer:
            self.score += 1
        else:
            self.score -= 1
            # If incorrect, add the correct country to the incorrect list to revisit later
            correct_country_obj = [c for c in self.countries if c["name"]["common"] == self.correct_answer]
            if correct_country_obj:
                self.incorrect_countries.append(correct_country_obj[0])

        self.score_label.configure(text=f"Score: {self.score}")
        self.next_question()

    def end_game(self):
        messagebox.showinfo("Game Over", f"Final Score: {self.score}")
        self.destroy()

if __name__ == "__main__":
    game = FlagGame()
    game.mainloop()
