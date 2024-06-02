from customtkinter import *
import math
from PIL import Image

#------------------pop up----------------------------
def popup():
    window.deiconify()
    window.lift()
    window.focus_force()

#-----------------Constants--------------------------
Work_min = 25
Short_min_break = 5
Long_min_break = 25
reps = 0
timer = None

#------------------Reset-----------------------------
def reset_timer():
    window.after_cancel(timer)
    title_label.configure(text="Timer")
    image_label.configure(text="00:00")
    check_mark.configure(text="")
    global reps
    reps = 0


#------------------Timer------------------------------
def start_timer():
    global reps
    reps += 1

    Work_min_sec = Work_min * 60
    Short_min_break_sec = Short_min_break * 60
    Long_min_break_sec = Long_min_break * 60
    

    if reps % 2 == 0 and reps % 8 != 0:
        title_label.configure(text="Short break", fg_color="Red")
        count_down(Short_min_break_sec)
    if reps % 8 == 0:
        title_label.configure(text="Long break", fg_color="Blue")
        count_down(Long_min_break_sec)
    if reps % 2 == 1:
        title_label.configure(text="Work", fg_color="Green")
        count_down(Work_min_sec)


#------------------Countdown--------------------------
def count_down(count):
    count_min = math.floor(count/60)
    count_sec = count % 60
    if count_sec < 10 :
        count_sec = f"0{count_sec}"

    image_label.configure(text = f"{count_min}:{count_sec}")
    if count > 0:
        global timer
        timer =  window.after(1000,count_down,count - 1)
    else:
        popup()
        start_timer()
        mark = ""
        work_sessions = math.floor(reps/2)
        for _ in range(work_sessions):
            mark += "✓"
            check_mark.configure(text=mark)


#-------------------------UI--------------------------
window = CTk()
window.title("Pomodoro")
window.config(padx= 50, pady= 50)
window.geometry("610x500")
set_appearance_mode("system")

title_label = CTkLabel(master=window, text="Timer", fg_color="transparent", corner_radius=20, font=("courier",35))
title_label.grid(column=1,row=0)


my_image = CTkImage(light_image=Image.open("pomodoro/tomato.gif"),dark_image=Image.open("pomodoro/tomato.gif"),size=(280, 280))

image_label = CTkLabel(master=window, image=my_image, text="00:00",font=("courier",35,"bold"))
image_label.grid(column=1, row=1)


start_button = CTkButton(master=window, text="Start",fg_color="transparent",border_color="#fffff",corner_radius=20, command=start_timer)
start_button.grid(column=0, row=2)

reset_button = CTkButton(master=window, text="Reset",fg_color="transparent",border_color="#ffff",corner_radius=20, command=reset_timer)
reset_button.grid(column=2, row=2)

check_mark = CTkLabel(master=window,fg_color="green")
check_mark.grid(column=1, row=2)


window.mainloop() 