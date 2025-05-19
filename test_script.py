import tkinter as tk
from tkinter import ttk, font, filedialog
import sys
import io
import black

# ---------- Functions ----------

def go_to_learning():
    hide_all()
    learn_screen.pack(fill=tk.BOTH, expand=True)

def go_to_testing():
    hide_all()
    testing_screen.pack(fill=tk.BOTH, expand=True)

def go_to_optimizer():
    hide_all()
    optimizer_screen.pack(fill=tk.BOTH, expand=True)

def back_to_welcome():
    hide_all()
    welcome_screen.pack(fill=tk.BOTH, expand=True)

def hide_all():
    welcome_screen.pack_forget()
    learn_screen.pack_forget()
    testing_screen.pack_forget()
    optimizer_screen.pack_forget()

def execute_code():
    code = input_text.get("1.0", tk.END)
    output_box.config(state=tk.NORMAL)
    output_box.delete("1.0", tk.END)

    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()

    try:
        exec(code, globals())
        output = redirected_output.getvalue()
        output_box.insert(tk.END, output)
    except Exception as e:
        output_box.insert(tk.END, f"Error: {e}")
    finally:
        sys.stdout = old_stdout

    output_box.config(state=tk.DISABLED)

def optimize_code():
    raw_code = optimizer_input.get("1.0", tk.END).strip()
    optimizer_output.config(state=tk.NORMAL)
    optimizer_output.delete("1.0", tk.END)

    if not raw_code:
        optimizer_output.insert(tk.END, "⚠️ Please enter some Python code to optimize.")
    else:
        try:
            optimized_code = black.format_str(raw_code, mode=black.FileMode())
            optimizer_output.insert(tk.END, optimized_code)
        except Exception as e:
            optimizer_output.insert(tk.END, f"❌ Error during optimization:\n{e}")

    optimizer_output.config(state=tk.DISABLED)

def copy_to_clipboard():
    optimized_code = optimizer_output.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(optimized_code)
    root.update()

def download_optimized_code():
    optimized_code = optimizer_output.get("1.0", tk.END)
    if not optimized_code.strip():
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".py",
        filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
        title="Save Optimized Code"
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(optimized_code)

def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def toggle_section(frame):
    if frame.winfo_viewable():
        frame.pack_forget()
    else:
        frame.pack(fill="x", padx=20, pady=(0, 10))

# ---------- Styling ----------

root = tk.Tk()
root.title("🔥 Mini Compiler - Python Interpreter 🔥")
root.geometry("1200x700")
root.config(bg="#f2f2f2")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                font=("Segoe UI", 12, "bold"),
                padding=10,
                relief="flat",
                background="#4CAF50",
                foreground="white")
style.map("TButton", background=[("active", "#45a049")])

default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Segoe UI", size=12)

# ---------- Updated Welcome Screen ----------

import time
import threading

def fade_in(widget, delay=10, steps=20):
    def _fade():
        for i in range(steps + 1):
            alpha = i / steps
            widget.update()
            widget.attributes('-alpha', alpha)
            time.sleep(delay / 1000)
    threading.Thread(target=_fade).start()

# ---------- Welcome Screen Upgrade ----------
def on_enter(event):
    event.widget.config(bg="#0D47A1")

def on_leave(event):
    event.widget.config(bg="#1976D2")

welcome_screen = tk.Frame(root, bg="#1E1E2F")
welcome_screen.pack(fill=tk.BOTH, expand=True)

root.after(100, lambda: fade_in(root))

# Header
tk.Label(
    welcome_screen,
    text="🔥 Mini Compiler - Python Interpreter 🔥",
    font=("Segoe UI", 28, "bold"),
    bg="#1E1E2F",
    fg="#FFD700"
).pack(pady=(30, 10))

tk.Label(
    welcome_screen,
    text="Learn, test and optimize Python code interactively.",
    font=("Segoe UI", 16),
    bg="#1E1E2F",
    fg="#DDDDDD"
).pack(pady=(0, 20))

tk.Label(
    welcome_screen,
    text="Project Team:\nMayank Singh, Piyush Kumar, Kartik Kapri, Kumkum Pandey",
    font=("Segoe UI", 12, "italic"),
    bg="#1E1E2F",
    fg="#BBBBBB"
).pack(pady=(0, 30))

# Navigation Buttons
nav_buttons = tk.Frame(welcome_screen, bg="#1E1E2F")
nav_buttons.pack(pady=10)

for i, (text, cmd) in enumerate([
    ("📘 Learn Python", go_to_learning),
    ("🧪 Test Your Skills", go_to_testing),
    ("🚀 Optimize Code", go_to_optimizer),
]):
    btn = tk.Button(
        nav_buttons, text=text, font=("Segoe UI", 13, "bold"),
        bg="#1976D2", fg="white", activebackground="#1565C0", cursor="hand2",
        padx=20, pady=10, relief="flat", command=cmd
    )
    btn.grid(row=0, column=i, padx=15)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# Topics Grid
topic_frame = tk.LabelFrame(
    welcome_screen, text="📚 Python Topics", font=("Segoe UI", 14, "bold"),
    bg="#292A3E", fg="#FFC107", bd=2, relief="ridge", padx=20, pady=10
)
topic_frame.pack(pady=30, padx=30, fill="both", expand=True)

topics = [
    "1. Variables & Data Types", "2. Operators", "3. Conditional Statements",
    "4. Loops", "5. Functions", "6. Data Structures",
    "7. File Handling", "8. Object-Oriented Programming",
    "9. Exception Handling", "10. Modules & Packages"
]

def on_topic_click(label):
    label.config(bg="#4CAF50", fg="white")
    root.after(500, lambda: label.config(bg="#37474F", fg="#FFC107"))

for i, topic in enumerate(topics):
    lbl = tk.Label(
        topic_frame, text=f"📌 {topic}", bg="#37474F", fg="#FFC107",
        font=("Segoe UI", 12, "bold"), padx=10, pady=5,
        anchor="w", cursor="hand2"
    )
    lbl.grid(row=i//2, column=i%2, sticky="we", padx=10, pady=5)
    lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg="#546E7A"))
    lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg="#37474F"))
    lbl.bind("<Button-1>", lambda e, l=lbl: on_topic_click(l))

# End of Welcome Screen Upgrade


# ---------- Learn Python Screen ----------

learn_screen = tk.Frame(root, bg="#E3F2FD")

tk.Label(learn_screen, text="📘 Learn Python", font=("Segoe UI", 22, "bold"),
         bg="#E3F2FD", fg="#0D47A1").pack(pady=20)

scroll_frame = tk.Frame(learn_screen)
scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas = tk.Canvas(scroll_frame, bg="#ffffff", highlightthickness=0)
scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
scrollable_content = tk.Frame(canvas, bg="#ffffff")

canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
scrollable_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
canvas.bind_all("<MouseWheel>", on_mousewheel)

sections = {
    "🔤 Variables & Data Types": "Python supports various data types like int, float, string, and boolean.",
    "🔁 Loops": "Use 'for' or 'while' loops to iterate over sequences or repeat actions.",
    "📦 Functions": "Functions help you reuse code. Define using 'def'.",
    "📄 File Handling": "Python can open, read, and write files using the 'open' function.",
    "🧪 Exception Handling": "Use try-except blocks to manage errors gracefully."
}

for title, desc in sections.items():
    container = tk.Frame(scrollable_content, bg="#E3F2FD", bd=1, relief="solid")
    title_label = tk.Label(container, text=title, font=("Segoe UI", 14, "bold"),
                           bg="#C5CAE9", fg="#1A237E", cursor="hand2", anchor="w", padx=10)
    title_label.pack(fill="x")

    content = tk.Label(container, text=desc, font=("Segoe UI", 12),
                       wraplength=1000, justify="left", bg="#E8EAF6", anchor="w", padx=10)
    content.pack_forget()

    title_label.bind("<Button-1>", lambda e, frame=content: toggle_section(frame))
    container.pack(fill="x", padx=20, pady=10)

ttk.Button(learn_screen, text="🔙 Back", command=back_to_welcome).pack(pady=10)

# ---------- Testing Screen ----------

import keyword
import re

# ---------- Updated Testing Screen with Syntax Highlighting ----------

testing_screen = tk.Frame(root, bg="#F1F8E9")

tk.Label(testing_screen, text="🧪 Python Testing Module",
         font=("Segoe UI", 22, "bold"), bg="#F1F8E9", fg="#2E7D32").pack(pady=20)

editor_output_pane = tk.PanedWindow(testing_screen, orient=tk.HORIZONTAL, sashwidth=5)
editor_output_pane.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

# -------- Left: Code Editor --------
editor_frame = tk.Frame(editor_output_pane, bg="#1E1E1E")
editor_output_pane.add(editor_frame, stretch="always")

tk.Label(editor_frame, text="✍️ Code Editor", font=("Segoe UI", 14, "bold"),
         bg="#1E1E1E", fg="#81C784", anchor="w").pack(fill="x", padx=10, pady=(10, 0))

input_text = tk.Text(editor_frame, height=20, font=("Consolas", 13), wrap="none",
                     bg="#2E2E2E", fg="white", insertbackground="white", undo=True)
input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Syntax Highlighting Tags
input_text.tag_configure("keyword", foreground="#C792EA")
input_text.tag_configure("string", foreground="#F78C6C")
input_text.tag_configure("comment", foreground="#546E7A")

# Syntax Highlighting Logic
def highlight_syntax(event=None):
    code = input_text.get("1.0", "end-1c")
    input_text.tag_remove("keyword", "1.0", tk.END)
    input_text.tag_remove("string", "1.0", tk.END)
    input_text.tag_remove("comment", "1.0", tk.END)

    for match in re.finditer(r'\b(' + r'|'.join(keyword.kwlist) + r')\b', code):
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        input_text.tag_add("keyword", start, end)

    for match in re.finditer(r'(\".*?\"|\'.*?\')', code):
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        input_text.tag_add("string", start, end)

    for match in re.finditer(r'#.*', code):
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        input_text.tag_add("comment", start, end)

input_text.bind("<KeyRelease>", highlight_syntax)

# -------- Right: Output Console --------
output_frame = tk.Frame(editor_output_pane, bg="#1E1E1E")
editor_output_pane.add(output_frame, stretch="always")

tk.Label(output_frame, text="📜 Output Console", font=("Segoe UI", 14, "bold"),
         bg="#1E1E1E", fg="#FFB74D", anchor="w").pack(fill="x", padx=10, pady=(10, 0))

output_box = tk.Text(output_frame, height=20, font=("Consolas", 13), wrap="none",
                     state=tk.DISABLED, bg="#263238", fg="#ECEFF1", insertbackground="white")
output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# -------- Bottom Controls --------
button_frame = tk.Frame(testing_screen, bg="#F1F8E9")
button_frame.pack(pady=10)

ttk.Button(button_frame, text="▶ Run Code", command=execute_code).grid(row=0, column=0, padx=10)
ttk.Button(button_frame, text="🔙 Back", command=back_to_welcome).grid(row=0, column=1, padx=10)

# ---------- Optimizer Screen ----------

optimizer_screen = tk.Frame(root, bg="#f3e5f5")

tk.Label(optimizer_screen, text="🚀 Python Code Optimizer ",
         font=("Segoe UI", 22, "bold"), bg="#f3e5f5", fg="#4A148C").pack(pady=20)

input_frame = tk.Frame(optimizer_screen, bg="#f3e5f5")
input_frame.pack(fill=tk.BOTH, expand=True, padx=10)

tk.Label(input_frame, text="📝 Enter Code:", font=("Segoe UI", 13, "bold"),
         bg="#f3e5f5", fg="#6A1B9A").pack(anchor="w")

optimizer_input = tk.Text(input_frame, height=10, font=("Consolas", 12), wrap="word",
                          bg="#fff", fg="#000", insertbackground="black")
optimizer_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

tk.Label(input_frame, text="✅ Optimized Code:", font=("Segoe UI", 13, "bold"),
         bg="#f3e5f5", fg="#4A148C").pack(anchor="w", pady=(10, 0))

optimizer_output = tk.Text(input_frame, height=10, font=("Consolas", 12), wrap="word",
                           state=tk.DISABLED, bg="#e1bee7", fg="#1A1A1A", insertbackground="black")
optimizer_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

button_frame = tk.Frame(optimizer_screen, bg="#f3e5f5")
button_frame.pack(pady=10)

ttk.Button(button_frame, text="🚀 Optimize Code", command=optimize_code).grid(row=0, column=0, padx=10)
ttk.Button(button_frame, text="📋 Copy to Clipboard", command=copy_to_clipboard).grid(row=0, column=1, padx=10)
ttk.Button(button_frame, text="💾 Download Code", command=download_optimized_code).grid(row=0, column=2, padx=10)
ttk.Button(button_frame, text="🔙 Back", command=back_to_welcome).grid(row=0, column=3, padx=10)

# ----------
root.mainloop()
