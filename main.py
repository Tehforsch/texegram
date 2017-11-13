#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, InlineQueryHandler, Filters
import os
import logging
import subprocess

def parseMessage(bot, update):
    content = update.message.text
    pictureFileName = parseLatex(update.effective_user, content)
    if pictureFileName is not None:
        bot.send_photo(chat_id=update.effective_chat.id, photo=open(pictureFileName, 'rb'))

def parseLatex(user, code):
    parsingFolder = os.path.join(latexFolderName, str(user.id))
    ensureFolderExists(parsingFolder)
    latexFile = os.path.join(parsingFolder, latexFileName)
    with open(latexFile, "w") as f:
        content = getLatexContent(code)
        f.write(content)
    return executeLatex(latexFile)

def getLatexContent(code):
    lines = preamble + [
            "\\begin{document}",
            "\\begin{equation*}",
            code,
            "\\end{equation*}",
            "\\end{document}"
            ]
    return "\n".join(lines)

def executeLatex(latexFile):
    path, filename = os.path.split(latexFile)
    # Parse LaTeX
    command = "latex --interaction=nonstopmode {}".format(filename)
    returncode, out, err = runCommand(command, path=path)
    # Convert dvi to png
    dviFileName = os.path.splitext(filename)[0] + ".dvi"
    pngFileName = os.path.splitext(filename)[0] + ".png"
    command = "convert -density 350 -geometry 200% {} {}".format(dviFileName, pngFileName)
    returncode, out, err = runCommand(command, path=path)
    print(returncode, out, err)
    pngFile = os.path.join(path, pngFileName)
    assert os.path.isfile(pngFile)
    return pngFile

def ensureFolderExists(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

def runCommand(command, path = None):
    mainPath = os.getcwd()
    os.chdir(path)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate() 
    os.chdir(mainPath)
    return p.returncode, stdout, stderr

def readPreamble():
    with open(os.path.join(latexFolderName, preambleFileName), "r") as f:
        return [l.replace("\n", "") for l in f.readlines()]

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    with open("apiToken", "r") as f:
        token = f.readlines()[0].replace("\n", "")
    updater = Updater(token)

    dispatcher = updater.dispatcher
    # dispatcher.add_handler(MessageHandler(Filters.text, parseMessage))
    dispatcher.add_handler(InlineQueryHandler(parseMessage))
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

latexFolderName = "latex"
latexFileName = "eq.tex"
preambleFileName = "preamble.tex"
preamble = readPreamble()

if __name__ == '__main__':
    main()
