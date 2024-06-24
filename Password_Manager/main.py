import customtkinter
from tkinter import *
from tkinter import messagebox
from random import choice, randint, shuffle
import pyperclip
import json
from security import *
from cryptography.fernet import Fernet
import sqlite3
from PIL import Image

# ---------------------------- PASSWORD GENERATOR ------------------------------- #

def generate_password():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_letters = [choice(letters) for _ in range(randint(8, 10))]
    password_symbols = [choice(symbols) for _ in range(randint(2, 4))]
    password_numbers = [choice(numbers) for _ in range(randint(2, 4))]

    password_list = password_letters + password_symbols + password_numbers
    shuffle(password_list)

    password = "".join(password_list)
    password_entry.delete(0, END)
    password_entry.insert(0, password)
    pyperclip.copy(password)

# ---------------------------- SAVE PASSWORD ------------------------------- #
def save():
    def key_store():
        # Generate a cryptography key
        key = (Fernet.generate_key()).decode('utf-8')       
        cipher = Fernet(key)
        
        # Get the website, email, and password entries
        website = hash_maker(website_entry_tab1.get().lower())
        email = email_entry.get()
        password = password_entry.get()
        new_data = {
            website: {
                "key": key  # Save hashed website and Fernet key in json file
            }
        }

        if len(website) == 0 or len(password) == 0:
            messagebox.showinfo(title="Oops", message="Please make sure you haven't left any fields empty.")
        else:
            # Load existing data from JSON file or create new one if not found
            try:
                with open("data.json", "r") as data_file:
                    data = json.load(data_file)
            except FileNotFoundError:
                with open("data.json", "w") as data_file:
                    json.dump(new_data, data_file, indent=4)
            else:
                # Update old data with new data
                data.update(new_data)

                with open("data.json", "w") as data_file:
                    json.dump(data, data_file, indent=4)
            finally:
                website_entry_tab1.delete(0, END)
                password_entry.delete(0, END)
                email_entry.delete(0, END)

            # Connect to the SQLite database
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS passwords
                         (website VARCHAR (255), username VARCHAR (255), password VARCHAR (255))''')
            conn.commit()

            # Encrypt the email and password
            encrypted_password = cipher.encrypt(password.encode('utf-8')).decode('utf-8')
            encrypted_email = cipher.encrypt(email.encode('utf-8')).decode('utf-8')

            # Check if the website already exists in the database
            c.execute("SELECT * FROM passwords WHERE website=?", (website,))
            result = c.fetchone()

            if result:
                # Update the existing record
                c.execute("UPDATE passwords SET username=?, password=? WHERE website=?", (encrypted_email, encrypted_password, website))
            else:
                # Insert a new record
                c.execute("INSERT INTO passwords VALUES (?, ?, ?)", (website, encrypted_email, encrypted_password))

            conn.commit()
            conn.close()

    key_store()

# ---------------------------- FIND PASSWORD ------------------------------- #
def find_password():
    website = website_entry_tab2.get()
    website_hashed = hash_maker(website_entry_tab2.get().lower())
    try:
        with open("data.json") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Error", message="No Data File Found.")
    else:
        if website_hashed in data:
            password_key = data[website_hashed]["key"] #Gets key

            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM passwords WHERE website=?", (website_hashed,))
            result = c.fetchone()
            
            cipher_suite = Fernet(password_key)
            decrypted_password = cipher_suite.decrypt(result[2].encode()).decode()#Decodes the password
            decrypted_username = cipher_suite.decrypt(result[1].encode()).decode()
            messagebox.showinfo(title=website, message=f"Email: {decrypted_username}\nPassword: {decrypted_password}")
        else:
            messagebox.showinfo(title="Error", message=f"No details for {website} exists.")

# ---------------------------- TOGGLE PASSWORD VISIBILITY ------------------------------- #
def toggle_password_visibility(entry, show_password):
    if show_password.get():
        entry.configure(show="")
    else:
        entry.configure(show="*")

# ---------------------------- UI SETUP ------------------------------- #

window = customtkinter.CTk()
window.title("Password Manager")
window.config(padx=50, pady=50)
window.geometry("700x700")
window.maxsize(700,700)
customtkinter.set_appearance_mode("system")
my_tab = customtkinter.CTkTabview(window,width=700,height=600,corner_radius=20)
my_tab.pack(pady=10)

tab1 = my_tab.add("Add")
tab2 = my_tab.add("Search")

my_image = customtkinter.CTkImage(light_image=Image.open("Password_Manager/logo.png"),dark_image=Image.open("Password_Manager/logo.png"),size=(280, 280))
img_tab1 = customtkinter.CTkLabel(master=tab1, image=my_image, text="")
img_tab1.pack()

img_tab2 = customtkinter.CTkLabel(master=tab2, image=my_image, text="")
img_tab2.pack()

website_label_tab1 = customtkinter.CTkLabel(master=tab1,text="Website:")
website_label_tab1.place(relx=0.2,rely=0.55, anchor=CENTER)

website_label_tab2 = customtkinter.CTkLabel(master=tab2,text="Website:")
website_label_tab2.place(relx=0.2,rely=0.65, anchor=CENTER)

email_label = customtkinter.CTkLabel(master=tab1,text="Email/Username:")
email_label.place(relx=0.15,rely=0.65, anchor=CENTER)

password_label = customtkinter.CTkLabel(master=tab1,text="Password:")
password_label.place(relx=0.2,rely=0.75, anchor=CENTER)

website_entry_tab1 = customtkinter.CTkEntry(master=tab1,width=250,corner_radius=20)
website_entry_tab1.place(relx=0.5,rely=0.55,anchor=CENTER)
website_entry_tab1.focus()

website_entry_tab2 = customtkinter.CTkEntry(master=tab2,width=300,corner_radius=20)
website_entry_tab2.place(relx=0.5,rely=0.65,anchor=CENTER)
website_entry_tab2.focus()

email_entry = customtkinter.CTkEntry(master=tab1,width=390, corner_radius=20)
email_entry.place(relx=0.62,rely=0.65, anchor = CENTER)

password_entry = customtkinter.CTkEntry(master=tab1,width=250, corner_radius=20, show="*")
password_entry.place(relx=0.5,rely=0.75, anchor=CENTER)

show_password_var = IntVar(value=0)
show_password_checkbutton = customtkinter.CTkCheckBox(master=tab1,text="show password",variable=show_password_var, command=lambda: toggle_password_visibility(password_entry, show_password_var))
show_password_checkbutton.place(relx=0.75, rely=0.75, anchor=W)

search_button = customtkinter.CTkButton(master=tab2,text="Search", width=190, command=find_password, corner_radius=20,border_width=1, fg_color="#4158D0",border_color="white")
search_button.place(relx=0.5,rely=0.75, anchor=CENTER)

generate_password_button = customtkinter.CTkButton(master=tab1,text="Generate Password", command=generate_password,border_width=1,fg_color="#4158D0",corner_radius=20,border_color="white")
generate_password_button.place(relx=0.85,rely=0.83, anchor=CENTER)

add_button = customtkinter.CTkButton(master=tab1,text="Add", width=300, command=save,corner_radius=20,fg_color="#4158D0",border_color="white")
add_button.place(relx=0.55,rely=0.95, anchor=CENTER)

window.mainloop()
