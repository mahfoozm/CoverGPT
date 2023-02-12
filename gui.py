import os, re, subprocess, platform
import customtkinter
import threading, asyncio
import tkinter.filedialog
import gptex
from PyPDF2 import PdfReader

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # configure window
        self.title("CoverGPT")
        self.geometry(f"{800}x{480}")
        customtkinter.set_widget_scaling(1.2)

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="CoverGPT", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.home_button_event, text="Home")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.sign_in_event, text="Login")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.settings_button_event, text="User Info")
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Full job posting...")
        self.entry.grid(row=3, column=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self, text="Generate", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: threading.Thread(target=self.send_job_listing_threaded).start())
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create company entry
        self.company_entry = customtkinter.CTkEntry(self, placeholder_text="Company name...")
        self.company_entry.grid(row=3, column=1, padx=(20, 0), pady=(20, 20), sticky="nsew")

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=340)
        self.textbox.grid(row=0, column=1, columnspan=3, padx=(0, 0), pady=(0, 0), sticky="nsew")

        # create slider and progressbar frame
        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.grid(row=1, column=1, columnspan=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
        self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.grid(row=3, column=0, padx=(20, 20), pady=(10, 10), sticky="ew")

        # create address fields, and resume upload button
        self.address1_entry = customtkinter.CTkEntry(self, placeholder_text="Company address...")
        self.address1_entry.grid(row=2, column=1, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.address2_entry = customtkinter.CTkEntry(self, placeholder_text="City, state, zip...")
        self.address2_entry.grid(row=2, column=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.main_button_1 = customtkinter.CTkButton(master=self, text="Upload Resume", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.upload_resume)
        self.main_button_1.grid(row=2, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("120%")
        self.progressbar_1.configure(mode="indeterminnate")
        self.textbox.insert("0.0", "CoverGPT, a cover letter generator powered by GPT-3.\n\n")
        self.textbox.insert("end", "Please login and set your user info before generating (see github page).\n\n\n")


    def send_job_listing_threaded(self):
        asyncio.run(self.send_job_listing())

    async def send_job_listing(self):
        if self.company_entry.get() and self.entry.get() == "":
            self.textbox.insert("end", "Please enter a job listing and company name.\n")
            return

        script_dir = os.path.dirname(os.path.realpath(__file__))
        login_file = os.path.join(script_dir, "login")
        settings_file = os.path.join(script_dir, "settings")

        if not os.path.exists(login_file):
            self.textbox.insert("end", "Please sign in.\n")
            return
        
        if not os.path.exists(settings_file):
            self.textbox.insert("end", "Please set your user info.\n")
            return

        job_listing = self.entry.get()
        company_name = self.company_entry.get()
        address1 = self.address1_entry.get()
        address2 = self.address2_entry.get()

        self.progressbar_1.start()
        self.textbox.insert("end", "\nGenerating cover letter...\n")

        try:
            await gptex.generateCoverLetter(job_listing, company_name, address1, address2)
        except Exception as e:
            self.textbox.insert("end", "\nError: " + str(e) + ". See terminal for more details.\n")
            self.progressbar_1.stop()
            return

        self.progressbar_1.stop()
        self.textbox.insert("end", "\nCover letter for " + company_name + " generated.\n")
        current_dir = os.getcwd()
        os.chdir(script_dir)
        if platform.system() == "Windows":
            subprocess.run(["start", "coverletter.pdf"], shell=True)
        else:
            subprocess.run(["open", "coverletter.pdf"])
        os.chdir(current_dir)


    def home_button_event(self):
        self.textbox.insert("end", "this button might do something in the future idrk\n")


    def upload_resume(self):
        resume_path = tkinter.filedialog.askopenfilename(title="Select Resume", filetypes=(("pdf files", "*.pdf"), ("all files", "*.*")))
        if resume_path == "":
            return

        resume = open(resume_path, "rb")
        reader = PdfReader(resume)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        rawResume_path = os.path.join(dir_path, "rawresume")
        rawResume = open(rawResume_path, "w", encoding="UTF-8")

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            page_text = re.sub(r'[^\x00-\x7F]+', '', page_text)
            rawResume.write(page_text)
        resume.close()
        rawResume.close()


    def sign_in_event(self):
        self.window = customtkinter.CTkToplevel(self)
        self.window.title("Sign In")
        self.window.geometry("320x200")

        self.userEmail_label = customtkinter.CTkLabel(self.window, text="Email:", anchor="w")
        self.userEmail_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.userEmail_entry = customtkinter.CTkEntry(self.window)
        self.userEmail_entry.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.userPass_label = customtkinter.CTkLabel(self.window, text="Password:", anchor="w")
        self.userPass_label.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.userPass_entry = customtkinter.CTkEntry(self.window, show="*")
        self.userPass_entry.grid(row=1, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.save_button = customtkinter.CTkButton(self.window, text="Save", command=self.save_login_button_event)
        self.save_button.grid(row=5, column=0, columnspan=2, padx=(20, 20), pady=(20, 20), sticky="nsew")

        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                self.userEmail_entry.insert(0, f.readline().rstrip())


    def settings_button_event(self):
        self.window = customtkinter.CTkToplevel(self)
        self.window.title("User Info")
        self.window.geometry("350x375")

        # create five text entries with labels to the left of them, add a save button to the bottom
        self.firstName_label = customtkinter.CTkLabel(self.window, text="First Name:", anchor="w")
        self.firstName_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.firstName_entry = customtkinter.CTkEntry(self.window)
        self.firstName_entry.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.lastName_label = customtkinter.CTkLabel(self.window, text="Last Name:", anchor="w")
        self.lastName_label.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.lastName_entry = customtkinter.CTkEntry(self.window)
        self.lastName_entry.grid(row=1, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.websiteUrl_label = customtkinter.CTkLabel(self.window, text="Website URL:", anchor="w")
        self.websiteUrl_label.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.websiteUrl_entry = customtkinter.CTkEntry(self.window)
        self.websiteUrl_entry.grid(row=2, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.email_label = customtkinter.CTkLabel(self.window, text="Email:", anchor="w")
        self.email_label.grid(row=3, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.email_entry = customtkinter.CTkEntry(self.window)
        self.email_entry.grid(row=3, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        
        self.phoneNumber_label = customtkinter.CTkLabel(self.window, text="Phone Number:", anchor="w")
        self.phoneNumber_label.grid(row=4, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.phoneNumber_entry = customtkinter.CTkEntry(self.window)
        self.phoneNumber_entry.grid(row=4, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.save_button = customtkinter.CTkButton(self.window, text="Save", command=self.save_user_button_event)
        self.save_button.grid(row=5, column=0, columnspan=2, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # read settings file and set text entries to the values in the file
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                self.firstName_entry.insert(0, f.readline().rstrip())
                self.lastName_entry.insert(0, f.readline().rstrip())
                self.websiteUrl_entry.insert(0, f.readline().rstrip())
                self.email_entry.insert(0, f.readline().rstrip())
                self.phoneNumber_entry.insert(0, f.readline().rstrip())


    def save_login_button_event(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(file_dir, "login")
        with open(file_path, "w") as f:
            f.write(self.userEmail_entry.get() + "\n")
            f.write(self.userPass_entry.get() + "\n")
        self.textbox.insert("end", "Login info saved.\n")
        self.window.destroy()


    def save_user_button_event(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(file_dir, "settings")
        with open(file_path, "w") as f:
            f.write(self.firstName_entry.get() + "\n")
            f.write(self.lastName_entry.get() + "\n")
            f.write(self.websiteUrl_entry.get() + "\n")
            f.write(self.email_entry.get() + "\n")
            f.write(self.phoneNumber_entry.get() + "\n")
        self.textbox.insert("end", "User info saved.\n")
        self.window.destroy()


    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)


    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


if __name__ == "__main__":
    app = App()
    app.mainloop()