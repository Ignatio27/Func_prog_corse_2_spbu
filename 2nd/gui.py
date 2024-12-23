import tkinter as tk
from tkinter import filedialog, messagebox
import os
from image_processor import parallel_process_images


class ImageProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка космических изображений")

        self.input_folder_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()

        tk.Label(root, text="Папка с изображениями:").pack(pady=5)
        tk.Entry(root, textvariable=self.input_folder_var, width=50).pack(pady=5)
        tk.Button(root, text="Выбрать папку", command=self.select_input_folder).pack(pady=5)

        tk.Label(root, text="Папка для сохранения изображений:").pack(pady=5)
        tk.Entry(root, textvariable=self.output_folder_var, width=50).pack(pady=5)
        tk.Button(root, text="Выбрать папку", command=self.select_output_folder).pack(pady=5)

        tk.Button(root, text="Запустить обработку", command=self.run_processing).pack(pady=20)

    def select_input_folder(self):
        folder = filedialog.askdirectory()
        self.input_folder_var.set(folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        self.output_folder_var.set(folder)

    def run_processing(self):
        input_folder = self.input_folder_var.get()
        output_folder = self.output_folder_var.get()

        if not input_folder or not output_folder:
            messagebox.showerror("Ошибка", "Пожалуйста, укажите пути к папкам.")
            return

        image_paths = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if
                       f.endswith(('.jpg', '.jpeg', '.png'))]

        if not image_paths:
            messagebox.showerror("Ошибка", "Не найдено изображений в указанной папке.")
            return

        df = parallel_process_images(image_paths, output_folder, num_workers=16)
        df.to_xml(os.path.join(output_folder, "astro_objects.xml"), index=False)

        messagebox.showinfo("Успех",
                            "Обработка завершена. Изображения сохранены, данные сохранены в 'astro_objects.xml'.")


def create_gui():
    root = tk.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    create_gui()
