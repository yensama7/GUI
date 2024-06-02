from customtkinter import *
from tkinter import messagebox
from random import choice, randint, shuffle
import pyperclip
import json
from security import *
from cryptography.fernet import Fernet
import sqlite3
from PIL import Image

# ---------------------------- PASSWORD GENERATOR ------------------------------- #

#Password Generator Project
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
    password_entry.insert(0, password)
    pyperclip.copy(password)

# ---------------------------- SAVE PASSWORD ------------------------------- #
def save():
    def key_store():
        #------------------------------cryptography key-------------------------------------------
        key = (Fernet.generate_key()).decode('utf-8')#creates cryptography key       
        cipher = Fernet(key)
        #------------------------------------json------------------------------------------
        website = hash_maker(website_entry.get().lower())
        email = email_entry.get()
        password = password_entry.get()
        new_data = {
            website: {
                "key" : key #saves hashed website and fernet key in json file
            }
        }

        if len(website) == 0 or len(password) == 0:
            messagebox.showinfo(title="Oops", message="Please make sure you haven't left any fields empty.")
        else:
            try:
                with open("data.json", "r") as data_file:
                    #Reading old data
                    data = json.load(data_file)
            except FileNotFoundError:
                with open("data.json", "w") as data_file:
                    json.dump(new_data, data_file, indent=4)
            else:
                #Updating old data with new data
                data.update(new_data)

                with open("data.json", "w") as data_file:
                    #Saving updated data
                    json.dump(data, data_file, indent=4)
            finally:
                website_entry.delete(0, END)
                password_entry.delete(0, END)
                email_entry.delete(0, END)

#----------------------database--------------------------  

        conn = sqlite3.connect('main.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS passwords
                 (website VARCHAR (255), username VARCHAR (255), password VARCHAR (255))''')
        conn.commit()

        encrypted_password = cipher.encrypt(password.encode('utf-8'))
        crypt_pass = encrypted_password.decode('utf-8')

        encrypted_email = cipher.encrypt(email.encode('utf-8'))
        crypt_email = encrypted_email.decode('utf-8')

        c.execute("INSERT INTO passwords VALUES (?, ?, ?)", (website, crypt_email, crypt_pass))
        conn.commit()# database to store the values encrypted 
        conn.close()



    key_store()
# ---------------------------- FIND PASSWORD ------------------------------- #
def find_password():
    website = website_entry.get()
    website_hashed = hash_maker(website_entry.get().lower())
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

# ---------------------------- UI SETUP ------------------------------- #

window = CTk()
window.title("Password Manager")
window.config(padx=50, pady=50)
window.geometry("600x600")
window.maxsize(600,600)
set_appearance_mode("system")


my_image = CTkImage(light_image=Image.open("Password_Manager/logo.png"),dark_image=Image.open("Password_Manager/logo.png"),size=(280, 280))
img = CTkLabel(master=window, image= my_image, text="")
img.grid(row= 0, column=1 )

#Labels
website_label = CTkLabel(master=window,text="Website:")
website_label.grid(row=1, column=0)

email_label = CTkLabel(master=window,text="Email/Username:")
email_label.grid(row=2, column=0)

password_label = CTkLabel(master=window,text="Password:")
password_label.grid(row=3, column=0)

#Entries
website_entry = CTkEntry(master=window,width=250,corner_radius=20)
website_entry.grid(row=1, column=1)
website_entry.focus()


email_entry = CTkEntry(master=window,width=400, corner_radius=20)
email_entry.grid(row=2, column=1, columnspan=2)

password_entry = CTkEntry(master=window,width=250, corner_radius=20)
password_entry.grid(row=3, column=1)

# Buttons
search_button = CTkButton(master=window,text="Search", width=13, command=find_password, corner_radius=20,border_width=1, fg_color="transparent",border_color="white")
search_button.grid(row=1, column=2)

generate_password_button = CTkButton(master=window,text="Generate Password", command=generate_password,border_width=1,fg_color="transparent",corner_radius=20,border_color="white")
generate_password_button.grid(row=3, column=2)

add_button = CTkButton(master=window,text="Add", width=300, command=save,corner_radius=20,fg_color="#4158D0",border_color="white")
add_button.place(relx = 0.5, rely= 0.8, anchor = "center")

window.mainloop()