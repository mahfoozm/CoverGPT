import subprocess
import fileinput
import main
from revChatGPT.ChatGPT import Chatbot

def generateCoverLetter(job_listing):

    f = open("session_token.txt", "r")
    session_token = f.read()

    message = "Write a cover letter for this job position: " + job_listing
    chatbot = Chatbot({
    "session_token": session_token
    }, conversation_id=None, parent_id=None)

    response = chatbot.ask(message, conversation_id=None, parent_id=None)

    content = response['message']
    paragraphs = content.split("\n\n")

    for i in range(1, len(paragraphs)-1):
        for line in fileinput.input("coverletter.tex", inplace=True, backup=".bak"):
            if line.strip() == "\\vspace{0.5cm}":
                print("\\lettercontent{" + paragraphs[i] + "}")
            print(line, end='')

    subprocess.run(["xelatex", "-interaction=batchmode", "coverletter.tex"])