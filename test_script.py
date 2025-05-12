import tkinter as tk
from tkinter import ttk, messagebox
from io import StringIO
import sys
import json
import os

from lexer1 import lexer
from my_parser1 import parser
from interpreter1 import Interpreter

# Load user data from JSON file
USER_DB_FILE = "users.json"

if os.path.exists(USER_DB_FILE):
    with open(USER_DB_FILE, "r") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = {}
else:
    users = {}

# ==============================
# Functions
# ==============================

def save_users_to_file():
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def execute_code():
    """ Execute user's code and display output """
    code = input_text.get("1.0", tk.END).strip()
    
    if not code:
        return  # Ignore empty input

    # Redirect stdout to capture output
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        # Remove leading/trailing spaces from each line
        code = "\n".join([line.strip() for line in code.split("\n") if line.strip()])

        # Lexical analysis
        lexer.input(code)
        tokens = list(lexer)

        # Parsing
        ast = parser.parse(code)
        if ast:
            interpreter = Interpreter()
            result = interpreter.interpret(ast)
            if result is not None:
                print("Return Value:", result)

        output_text = sys.stdout.getvalue().strip()
        if not output_text:
            output_text = "✅ Execution Completed. No output."

    except Exception as e:
        output_text = f"❌ Error: {str(e)}"

    finally:
        sys.stdout = old_stdout  # Restore stdout

    # Update output box
    output_box.config(state=tk.NORMAL)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, output_text)
    output_box.config(state=tk.DISABLED)

def go_to_learning():
    welcome_screen.pack_forget()
    learning_screen.pack(fill=tk.BOTH, expand=True)

def go_to_testing():
    welcome_screen.pack_forget()
    login_screen.pack(fill=tk.BOTH, expand=True)

def back_to_welcome():
    learning_screen.pack_forget()
    testing_screen.pack_forget()
    login_screen.pack_forget()
    welcome_screen.pack(fill=tk.BOTH, expand=True)

def show_testing_screen():
    login_screen.pack_forget()
    testing_screen.pack(fill=tk.BOTH, expand=True)

def login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    
    if username in users and users[username] == password:
        messagebox.showinfo("Login Successful", f"Welcome back, {username}!")
        show_testing_screen()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def signup():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    
    if not username or not password:
        messagebox.showwarning("Input Error", "Username and Password cannot be empty.")
        return

    if username in users:
        messagebox.showerror("Signup Failed", "Username already exists. Please login.")
    else:
        users[username] = password
        save_users_to_file()
        messagebox.showinfo("Signup Successful", f"Account created for {username}!")
        show_testing_screen()

# ==============================
# GUI Code
# ==============================

# Create main window
root = tk.Tk()
root.title("🔥 Mini Compiler - Python Interpreter 🔥")
root.geometry("1100x650")
root.config(bg="#FFCC33")

# ----------------- Welcome Screen -----------------
welcome_screen = tk.Frame(root, bg="#FFCC33")
welcome_screen.pack(fill=tk.BOTH, expand=True)

heading_label = tk.Label(welcome_screen, text="🔥 Mini Compiler - Python Interpreter 🔥", font=("Arial", 22, "bold"), bg="#FFCC33", fg="darkblue")
heading_label.pack(pady=20)

project_desc = tk.Label(welcome_screen, 
                        text="This is a Python-based mini compiler that allows you to learn and test Python skills. "
                             "Our goal is to provide a tool that helps you learn the basics of Python programming and test your skills "
                             "through an interactive platform. The project features a code editor, output display, and more.",
                        font=("Arial", 17), bg="#FFCC33", fg="black", justify=tk.LEFT, wraplength=800)
project_desc.pack(padx=20, pady=20, fill=tk.X)

team_label = tk.Label(welcome_screen, text="Project Team: \n\n1. Mayank Singh - Backend (Interpreter/Compiler)\n2. Piyush Shastri - Frontend (GUI)\n"
                                            "3. Kartik Kapri - Backend (Interpreter/Compiler)\n4. Kumkum Pandey - Frontend (GUI)",
                      font=("Arial", 14, "italic","bold"), bg="#FFCC33", fg="black", anchor="w")
team_label.pack(pady=10, padx=20, fill=tk.X)

button_frame = tk.Frame(welcome_screen, bg="#FFCC33")
button_frame.pack(pady=20)

learn_button = tk.Button(button_frame, text="Learn Python", command=go_to_learning, font=("Arial", 14, "bold"), bg="green", fg="white", width=15)
learn_button.pack(pady=10)

test_button = tk.Button(button_frame, text="Test Your Skills", command=go_to_testing, font=("Arial", 14, "bold"), bg="orange", fg="white", width=15)
test_button.pack(pady=10)

# ----------------- Login/Signup Screen -----------------
login_screen = tk.Frame(root, bg="lightblue")

login_label = tk.Label(login_screen, text="🔒 Login or Signup", font=("Arial", 22, "bold"), bg="lightblue", fg="darkblue")
login_label.pack(pady=20)

username_label = tk.Label(login_screen, text="Username:", font=("Arial", 16), bg="lightblue")
username_label.pack(pady=5)
username_entry = tk.Entry(login_screen, font=("Arial", 14))
username_entry.pack(pady=5)

password_label = tk.Label(login_screen, text="Password:", font=("Arial", 16), bg="lightblue")
password_label.pack(pady=5)
password_entry = tk.Entry(login_screen, show="*", font=("Arial", 14))
password_entry.pack(pady=5)

login_btn = tk.Button(login_screen, text="Login", command=login, font=("Arial", 14, "bold"), bg="green", fg="white", width=15)
login_btn.pack(pady=10)

signup_btn = tk.Button(login_screen, text="Signup", command=signup, font=("Arial", 14, "bold"), bg="purple", fg="white", width=15)
signup_btn.pack(pady=10)

back_btn_login = tk.Button(login_screen, text="Back to Welcome", command=back_to_welcome, font=("Arial", 12, "bold"), bg="red", fg="white")
back_btn_login.pack(pady=10)

# ----------------- Learning Screen -----------------
learning_screen = tk.Frame(root, bg="lightgreen")

learning_label = tk.Label(learning_screen, text="🔸 Python Learning Module 🔸", font=("Arial", 22, "bold"), bg="lightgreen", fg="darkgreen")
learning_label.pack(pady=20)

learning_content = tk.Label(learning_screen, text="🔹 Python Basics 🔹\n\n1. Introduction*: Python is an interpreted, high-level, general-purpose programming language. It's known for its readability and ease of use.\n"
                                                   "2. Variables & Data Types*: Python supports different data types like integers, floats, strings, and booleans. Variables are used to store values.\n"
                                                   "3. Functions*: Functions in Python are blocks of reusable code that can be called with different inputs.\n"
                                                   "4. Loops*: Loops are used to repeat a block of code multiple times. Python supports `for` and `while` loops.\n"
                                                   "5. Conditionals*: Conditional statements like `if`, `elif`, and `else` allow you to control the flow of your program.\n\n"
                                                   "🔹 Advanced Topics 🔹\n\n1. Classes & Objects*: Python is an object-oriented language, which means it allows the creation of classes and objects.\n"
                                                   "2. Exception Handling*: Python provides `try`, `except`, and `finally` blocks to handle exceptions during runtime.\n"
                                                   "3. File I/O*: Python can interact with files. You can read, write, and manipulate files using built-in functions.\n"
                                                   "4. Libraries (NumPy, Pandas)*: These libraries are used for data manipulation, analysis, and scientific computing.",
                            font=("Arial", 15), bg="lightgreen", fg="black", justify=tk.LEFT, wraplength=800)
learning_content.pack(padx=20, pady=20)

back_button_learning = tk.Button(learning_screen, text="Back to Welcome", command=back_to_welcome, font=("Arial", 12, "bold"), bg="red", fg="white")
back_button_learning.pack(pady=10)

# ----------------- Testing Screen -----------------
testing_screen = tk.Frame(root, bg="lightyellow")

testing_label = tk.Label(testing_screen, text="🔸 Python Testing Module 🔸", font=("Arial", 22, "bold"), bg="lightyellow", fg="darkorange")
testing_label.pack(pady=20)

main_frame = tk.Frame(testing_screen, bg="lightyellow")
main_frame.pack(pady=10, fill=tk.BOTH, expand=True)

paned_window = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashwidth=5, bg="lightyellow")
paned_window.pack(fill=tk.BOTH, expand=True)

left_frame = tk.Frame(paned_window, bg="#252526")
paned_window.add(left_frame, stretch="always")

tk.Label(left_frame, text="✍️ Code Editor:", font=("Arial", 14, "bold"), bg="#252526", fg="lightgreen").pack(anchor="w")

y_scrollbar = tk.Scrollbar(left_frame, orient=tk.VERTICAL)
x_scrollbar = tk.Scrollbar(left_frame, orient=tk.HORIZONTAL)

input_text = tk.Text(left_frame, height=18, font=("Courier", 12), wrap="none", bg="#1E1E1E", fg="white", insertbackground="white",
                     yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

y_scrollbar.config(command=input_text.yview)
x_scrollbar.config(command=input_text.xview)
y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

right_frame = tk.Frame(paned_window, bg="#252526")
paned_window.add(right_frame, stretch="always")

tk.Label(right_frame, text="📜 Output:", font=("Arial", 14, "bold"), bg="#252526", fg="orange").pack(anchor="w")

output_y_scrollbar = tk.Scrollbar(right_frame, orient=tk.VERTICAL)
output_x_scrollbar = tk.Scrollbar(right_frame, orient=tk.HORIZONTAL)

output_box = tk.Text(right_frame, height=18, font=("Courier", 12), wrap="none", state=tk.DISABLED, bg="#1E1E1E", fg="white", insertbackground="white",
                     yscrollcommand=output_y_scrollbar.set, xscrollcommand=output_x_scrollbar.set)
output_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

output_y_scrollbar.config(command=output_box.yview)
output_x_scrollbar.config(command=output_box.xview)
output_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

button_frame = tk.Frame(testing_screen, bg="lightyellow")
button_frame.pack(pady=5)

execute_button = tk.Button(button_frame, text="▶ Run Code", command=execute_code, font=("Arial", 14, "bold"), bg="blue", fg="white", width=15)
execute_button.pack(pady=5)

back_button_testing = tk.Button(button_frame, text="Back to Welcome", command=back_to_welcome, font=("Arial", 12, "bold"), bg="red", fg="white")
back_button_testing.pack(pady=5)

# ==============================
root.mainloop()
