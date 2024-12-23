import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

# Загрузка данных и обработка предпочтений
def load_books(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def calculate_rating(book, preferences):
    rating = 0
    if book['genre'].lower() in preferences['genres']:
        rating += 3
    if str(book['author'][0]).lower() in preferences['authors']:
        rating += 2

    for keyword in preferences['keywords']:
        if keyword in book['description'].lower():
            rating += 1

    if int(book.get('first_publish_year', 0)) >= preferences.get('min_year', 0):
        rating += 1
    return rating

def recommend_books(books, preferences):
    books_with_ratings = [
        {**book, "rating": calculate_rating(book, preferences)}
        for book in books
    ]
    return sorted(books_with_ratings, key=lambda b: b["rating"], reverse=True)

# Основной класс приложения
class BookRecommenderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Книжные рекомендации")
        self.geometry("800x800")
        self.books = load_books(r"books.json")
        self.to_read_list = []  # Список "Прочитать"
        self.create_widgets()

    def create_widgets(self):
        # Таблица для рекомендаций
        frame_table = tk.Frame(self, pady=10)
        frame_table.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(frame_table, columns=("Title", "Author", "Genre", "First Publish Year", "Rating"), show="headings")
        self.tree.heading("Title", text="Название")
        self.tree.heading("Author", text="Автор")
        self.tree.heading("Genre", text="Жанр")
        self.tree.heading("First Publish Year", text="Год публикации")
        self.tree.heading("Rating", text="Рейтинг")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Верхняя панель ввода предпочтений
        frame_input = tk.Frame(self, pady=10)
        frame_input.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_input, text="Жанры:", anchor="w", width=15).grid(row=0, column=0, padx=5, pady=5)
        self.entry_genres = ttk.Entry(frame_input, width=60)
        self.entry_genres.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Авторы:", anchor="w", width=15).grid(row=1, column=0, padx=5, pady=5)
        self.entry_authors = ttk.Entry(frame_input, width=60)
        self.entry_authors.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Ключевые слова:", anchor="w", width=15).grid(row=2, column=0, padx=5, pady=5)
        self.entry_keywords = ttk.Entry(frame_input, width=60)
        self.entry_keywords.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Минимальный год:", anchor="w", width=15).grid(row=3, column=0, padx=5, pady=5)
        self.entry_min_year = ttk.Entry(frame_input, width=60)
        self.entry_min_year.grid(row=3, column=1, padx=5, pady=5)

        btn_recommend = ttk.Button(frame_input, text="Рекомендовать", command=self.get_recommendations)
        btn_recommend.grid(row=4, column=1, pady=10, sticky="e")

        # Панель с кнопками
        frame_buttons = tk.Frame(self, pady=10)
        frame_buttons.pack(fill="x", padx=10, pady=5)

        btn_add_to_read = ttk.Button(frame_buttons, text="Добавить в список 'Прочитать'", command=self.add_to_read)
        btn_add_to_read.pack(side="left", padx=5)

        btn_save = ttk.Button(frame_buttons, text="Сохранить рекомендации", command=self.save_recommendations)
        btn_save.pack(side="right", padx=5)

        # Таблица для списка "Прочитать"
        frame_to_read = tk.Frame(self, pady=10)
        frame_to_read.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(frame_to_read, text="Список 'Прочитать'", anchor="w", font=("Arial", 14)).pack(pady=5)

        self.tree_to_read = ttk.Treeview(frame_to_read, columns=("Title", "Author", "Genre"), show="headings")
        self.tree_to_read.heading("Title", text="Название")
        self.tree_to_read.heading("Author", text="Автор")
        self.tree_to_read.heading("Genre", text="Жанр")
        self.tree_to_read.pack(fill="both", expand=True, padx=5, pady=5)

    def get_recommendations(self):
        genres = self.entry_genres.get().split(',')
        authors = self.entry_authors.get().split(',')
        keywords = self.entry_keywords.get().split(',')
        min_year = self.entry_min_year.get().strip()
        preferences = {
            "genres": [g.strip().lower() for g in genres if g.strip()],
            "authors": [a.strip().lower() for a in authors if a.strip()],
            "keywords": [k.strip().lower() for k in keywords if k.strip()],
            "min_year": int(min_year) if min_year.isdigit() else 0
        }
        recommendations = recommend_books(self.books, preferences)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for book in recommendations:
            self.tree.insert("", "end", values=(book["title"], book["author"], book["genre"], book["first_publish_year"], book["rating"]))

        if not recommendations:
            messagebox.showinfo("Результат", "Рекомендации не найдены.")

    def add_to_read(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Ошибка", "Выберите книгу из списка рекомендаций.")
            return

        for item in selected_items:
            book_data = self.tree.item(item)["values"]
            book = {"title": book_data[0], "author": book_data[1], "genre": book_data[2]}
            if book not in self.to_read_list:
                self.to_read_list.append(book)

        self.update_to_read_list()

    def update_to_read_list(self):
        for row in self.tree_to_read.get_children():
            self.tree_to_read.delete(row)

        for book in self.to_read_list:
            self.tree_to_read.insert("", "end", values=(book["title"], book["author"], book["genre"]))

    def save_recommendations(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        if not file_path:
            return

        recommendations = [
            self.tree.item(row)["values"]
            for row in self.tree.get_children()
        ]
        data = [{"title": r[0], "author": r[1], "genre": r[2], "first_publish_year": r[3], "rating": r[4]} for r in recommendations]
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Сохранение", f"Рекомендации сохранены в файл {file_path}.")


if __name__ == "__main__":
    app = BookRecommenderApp()
    app.mainloop()
