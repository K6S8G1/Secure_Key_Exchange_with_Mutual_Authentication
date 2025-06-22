import tkinter as tk
from tkinter import messagebox
import threading
from alice_backend import start_alice

def run_alice(message_text):
    try:
        start_alice(message_text)
        messagebox.showinfo("Sukces", "Wiadomość została wysłana!")
    except Exception as e:
        messagebox.showerror("Błąd", str(e))

def main_gui():
    root = tk.Tk()
    root.title("Alice – Bezpieczna wiadomość")

    tk.Label(root, text="Wiadomość do Boba:").pack(pady=5)
    message_entry = tk.Entry(root, width=50)
    message_entry.pack(pady=5)

    def send_msg():
        msg = message_entry.get()
        if msg.strip() == "":
            messagebox.showwarning("Uwaga", "Wiadomość nie może być pusta.")
        else:
            threading.Thread(target=run_alice, args=(msg,), daemon=True).start()

    tk.Button(root, text="Wyślij wiadomość", command=send_msg).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main_gui()
