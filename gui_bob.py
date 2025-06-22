import tkinter as tk
import threading
from bob_backend import start_bob

def main_gui():
    root = tk.Tk()
    root.title("Bob – Odbiorca wiadomości")

    log = tk.Text(root, height=20, width=60, wrap=tk.WORD)
    log.pack(padx=10, pady=10)

    def log_append(text):
        log.insert(tk.END, text + "\n")
        log.see(tk.END)

    def run_bob():
        threading.Thread(target=start_bob, args=(log_append,), daemon=True).start()

    tk.Button(root, text="Uruchom nasłuch", command=run_bob).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main_gui()
