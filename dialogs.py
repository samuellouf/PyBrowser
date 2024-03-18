"""PyBrowser's text"""
import json

class Dialogs():
    def __init__(self):
        self.language = None
    
    def setLanguage(self, language):
        self.language = language
        
    def getLanguage(self):
        return self.language
    
    def getLanguageDialogs(self, language = 'get'):
        if language == 'get':
            language = self.language
        
        lang = open('locales/' + language + '.json')
        return lang.read().replace('Ã©', 'é').replace('Ãª', 'ê').replace('Ã¨', 'è').replace('Ã®', 'î').replace('Ã€', 'À')
        
    def getDialog(self, dialog, language = 'get'):
        dialogs = self.getLanguageDialogs()
        dialogs = json.loads(dialogs)
        return dialogs[dialog]