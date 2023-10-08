# %%writefile modelo_booleano.py
#!usr/bin/bash python

import nltk
import sys

nltk.download("stopwords")
nltk.download('punkt')

base = sys.argv[1]
consult_file = sys.argv[2] 

print(base)
print(consult_file)

class Term():
    def __init__(self, value):
        self.value = value

class Expr():
    def __init__(self, kind):
        self.kind = kind
        self.left = None
        self.right = None

class Consult:
  def __init__(self, text, lexer):
        self.text = text
        self.keywords = {
            "|": "OR",
            "&": "AND",
            "!": "NOT",
        }
        self.lexer = lexer

  def generateAST(self):
    tokens = self.lexer.tokenize_text(self.text)
    ast = None
    lastNode = None
    find_next_position_term = False

    for i in range(1, len(tokens)):
      if (tokens[i] in self.keywords):
        expr = Expr(tokens[i])
        
        if (self.keywords[tokens[i]] == self.keywords['!'] or i == len(tokens) - 2):
          print("aaaa ")
          find_next_position_term = True
        else:
          find_next_position_term = False

        if (find_next_position_term):
          expr.left = Term(tokens[i + 1])
        else:
          expr.left = Term(tokens[i - 1])

        if (ast is None):
          ast = expr
        else:
          lastNode.right = expr
        lastNode = expr

    return ast

  def printAST(self, n, depth=0):
      if n:
        if isinstance(n, Term):
          print("  " * depth + n.value)
        elif isinstance(n.right, Expr):
          print("  " * depth + n.kind)
          self.printAST(n.left, depth + 1)
          self.printAST(n.right, depth + 1)

class BaseFile:
  def __init__(self, name, lexer):
        self.name = name
        self.terms = []
        self.tokens = []
        self.lexer = lexer

  def extract_terms(self):
    with open(self.name, 'r', encoding='utf-8') as f:
      text = f.read()
      self.tokens = self.lexer.tokenize_text(text)
      self.terms = self.remove_stopwords() 

  def remove_stopwords(self):
    stopwords = self.lexer.get_stopwords()
    clean_terms = []

    for term in self.tokens:
      if (not term in stopwords):
        clean_terms.append(term)

    return clean_terms

class TextLexer:
  def __init__(self, nltk):
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

    lexer = TextLexer(nltk)

    with open(base, 'r', encoding='utf-8') as f:
        for file in f.readlines():
            base_file = BaseFile(file.strip(), lexer)
            base_file.extract_terms()

    with open(consult_file, 'r', encoding='utf-8') as f:
      text = f.read()
      consult = Consult(text.strip(), lexer)
      print(consult.generateAST())

if __name__ == "__main__":
    main()
