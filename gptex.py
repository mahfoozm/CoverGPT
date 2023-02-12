import os, subprocess
import fileinput
import shutil
from revChatGPT.V2 import Chatbot

def replace_value(line, field, value):
    if field in line:
        line = line.replace(field, value)
    return line

async def generateCoverLetter(job_listing, company_name, address1, address2):
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # read user credentials from file
    api_key_file = os.path.join(script_dir, "login")
    with open(api_key_file, "r") as f:
        user_email = f.readline().strip()
        user_password = f.readline().strip()

    # read settings from file
    settings_file = os.path.join(script_dir, "settings")
    with open(settings_file, "r") as f:
        first_name = f.readline().strip()
        last_name = f.readline().strip()
        website_url = f.readline().strip()
        email = f.readline().strip()
        phone_number = f.readline().strip()

    # read resume from file
    rawresume_file = os.path.join(script_dir, "rawresume")
    if os.path.exists(rawresume_file):
        with open(rawresume_file, "r", encoding="UTF-8", errors='ignore') as f:
            resume = f.read()
        message = "Write a cover letter without a letter closing for this job position: " + company_name + " " + job_listing + "\n This is my resume: \n" + resume
        message = "".join(c for c in message if c <= "\uFFFF")
    else:
        message = "Write a cover letter without a letter closing for this job position: " + company_name + " " + job_listing

    print(message)
    chatbot = Chatbot(email=user_email, password=user_password)
    
    body = ""
    async for content in chatbot.ask(message):
        body += content["choices"][0]["text"].replace("<|im_end|>", "")
    print(body)

    paragraphs = body.split("\n\n")

    template_file = os.path.join(script_dir, "template.tex")
    coverletter_file = os.path.join(script_dir, "coverletter.tex")
    shutil.copyfile(template_file, coverletter_file)

    for line in fileinput.input(coverletter_file, inplace=True):
        switch = {
            "#firstName": first_name,
            "#lastName": last_name,
            "#websiteUrl": website_url,
            "#email": email,
            "#phoneNumber": phone_number,
            "#fullName": first_name + " " + last_name,
            "#address1": address1,
            "#address2": address2,
            "#companyName": company_name
        }
        for field, value in switch.items():
            line = replace_value(line, field, value)
        print(line, end='')

    for i in range(1, len(paragraphs) - 1):
        file_path = os.path.join(script_dir, "coverletter.tex")
        for line in fileinput.input(file_path, inplace=True, backup=".bak"):
            if line.strip() == "\\vspace{0.5cm}":
                print("\\lettercontent{" + paragraphs[i] + "}")
            print(line, end='')

    current_dir = os.getcwd()
    os.chdir(script_dir)
    subprocess.run(["xelatex", "-interaction=batchmode", os.path.join(script_dir, "coverletter.tex")])
    os.chdir(current_dir)