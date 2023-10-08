%%writefile modelo_booleano.py
#!usr/bin/bash python

import nltk
import sys

nltk.download("stopwords")
nltk.download('punkt')

base = sys.argv[1]
consult_file = sys.argv[2] 

print(base)
print(consult_file)

class BaseFile:
  def __init__(self, name):
        self.name = name
        self.terms = []
        self.tokens = []
        self.lexer = TextLexer()

  def extract_terms(self):
    with open(self.name, 'r', encoding='utf-8') as f:
      text = f.read()
      self.tokens = self.lexer.tokenize_text(text)
      self.terms = self.remove_stopwords() 
      print(self.terms)

  def remove_stopwords(self):
    stopwords = self.lexer.get_stopwords()
    clean_terms = []

    for term in self.tokens:
      if (not term in stopwords):
        clean_terms.append(term)

    return clean_terms

class TextLexer:
  def __init__(self):
        self.nltk = nltk

  def tokenize_text(self, text):
    return self.nltk.word_tokenize(text)

  def get_stopwords(self):
    stopwords_list = self.nltk.corpus.stopwords.words("portuguese")+[' ', '.', '...', ',', '!', '?', '\n', '\r\n']
    stopwords = {}

    for stopword in stopwords_list:
      stopwords[stopword] = stopword

    return stopwords

def main():
    if len(sys.argv) != 3:
        print("Usage: modelo_booleano.py <base_file> <consult_file>")
        sys.exit(1)

    base = sys.argv[1]
    consult_file = sys.argv[2]

    with open(base, 'r', encoding='utf-8') as f:
        for file in f.readlines():
            base_file = BaseFile(file.strip())
            base_file.extract_terms()

if __name__ == "__main__":
    main()
