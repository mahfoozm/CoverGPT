import os, subprocess
import fileinput
import shutil
from revChatGPT.Official import Chatbot

def replace_value(line, field, value):
    if field in line:
        line = line.replace(field, value)
    return line

def generateCoverLetter(job_listing, company_name, address1, address2):
    # read api key from file
    f = open("api_key", "r")
    api_key = f.read()
    f.close()

    # read settings from file
    f = open("settings", "r")
    first_name = f.readline().strip()
    last_name = f.readline().strip()
    website_url = f.readline().strip()
    email = f.readline().strip()
    phone_number = f.readline().strip()
    f.close()

    # read resume from file
    if os.path.exists("rawresume"):
        f = open("rawresume", "r", encoding="UTF-8", errors='ignore')
        resume = f.read()
        f.close()
        message = "Write a cover letter for this job position: " + company_name + " \n" + job_listing + "\n This is my resume: " + resume
        message = "".join(c for c in message if c <= "\uFFFF")
    else:
        message = "Write a cover letter for this job position: " + company_name + " \n" + job_listing

    print(message, 0.5)
    chatbot = Chatbot(api_key)
    response = chatbot.ask(message)

    content = response["choices"][0]["text"]
    print(content)

    paragraphs = content.split("\n\n")

    shutil.copyfile("template.tex", "coverletter.tex")

    for line in fileinput.input("coverletter.tex", inplace=True):
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

    for i in range(1, len(paragraphs)-1):
        for line in fileinput.input("coverletter.tex", inplace=True, backup=".bak"):
            if line.strip() == "\\vspace{0.5cm}":
                print("\\lettercontent{" + paragraphs[i] + "}")
            print(line, end='')

    subprocess.run(["xelatex", "-interaction=batchmode", "coverletter.tex"])