# add googlemaps wrapper to search for company address and add to the cover letter
import subprocess
import fileinput
import shutil
import gui
from revChatGPT.ChatGPT import Chatbot

def generateCoverLetter(job_listing, company_name):

    f = open("session_token.txt", "r")
    session_token = f.read()

    message = "Write a cover letter for this job position:" + company_name + job_listing
    chatbot = Chatbot({
    "session_token": session_token
    }, conversation_id=None, parent_id=None)

    response = chatbot.ask(message, conversation_id=None, parent_id=None)

    content = response['message']
    print(content)
    paragraphs = content.split("\n\n")

    shutil.copyfile("template.tex", "coverletter.tex")

    for line in fileinput.input("coverletter.tex", inplace=True):
        if "#companyName" in line:
            line = line.replace("#companyName", company_name)
        print(line, end='')

    for i in range(1, len(paragraphs)-1):
        for line in fileinput.input("coverletter.tex", inplace=True, backup=".bak"):
            if line.strip() == "\\vspace{0.5cm}":
                print("\\lettercontent{" + paragraphs[i] + "}")
            print(line, end='')

    subprocess.run(["xelatex", "-interaction=batchmode", "coverletter.tex"])