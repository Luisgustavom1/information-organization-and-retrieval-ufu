import nltk
import sys

nltk.download("stopwords")
nltk.download('punkt')
nltk.download("rslp")

def create_inverted_index(files):
  index_file = 'indice.txt'

  booleanModel = BooleanModel().create(files)

  with open(index_file, 'w') as f:
    # TODO: convert to string builder
    string = ''
    for term, tupls in booleanModel.items():
      string += f"{term}:"
      for tupl in tupls:
        string += f" {str(tupl[0])},{str(tupl[1])}"
      string += "\n"
    
    f.write(string)

  return booleanModel

class BooleanModel:
  def create(self, files):
      boolean_model = {}

      for i, file in enumerate(files):
        file_index = file.generate_boolean_model()
        for key, value in file_index.items():
            tupl = (i + 1, value)
            if (key in boolean_model):
              boolean_model[key].append(tupl)
            else:
              boolean_model[key] = [tupl]

      return boolean_model

class Term:
    def __init__(self, value):
        self.value = value

class Expr:
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

  def generate_ast(self):
    tokens = self.lexer.tokenize_text(self.text)
    ast = None
    lastNode = None
    find_next_position_term = False

    for i in range(1, len(tokens)):
      if (tokens[i] in self.keywords):
        expr = Expr(tokens[i])
        
        if (self.keywords[tokens[i]] == self.keywords['!'] or i == len(tokens) - 2):
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

class BaseFile:
  def __init__(self, name, lexer):
        self.name = name
        self.terms = []
        self.lexer = lexer

  def generate_boolean_model(self):
    self.extract_terms()
    boolean_model = {}

    for t in self.terms:
      radical = self.lexer.extract_radical(t)
      if (radical in boolean_model):
        boolean_model[radical] += 1
      else:
        boolean_model[radical] = 1

    return boolean_model

  def extract_terms(self):
    with open(self.name, 'r', encoding='utf-8') as f:
      text = f.read()
      tokens = self.extract_tokens(text)
      self.terms = self.remove_stopwords(tokens) 

  def extract_tokens(self, text):
    return self.lexer.tokenize_text(text)

  def remove_stopwords(self, tokens):
    stopwords = self.lexer.get_stopwords()
    clean_tokens = []

    for token in tokens:
      if (not token in stopwords):
        clean_tokens.append(token)

    return clean_tokens

class TextLexer:
  def __init__(self, nltk):
        self.nltk = nltk
  
  def extract_radical(self, term):
      extrator = nltk.stem.RSLPStemmer()
      return extrator.stem(term) 

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

    base_files = []

    with open(base, 'r', encoding='utf-8') as f:
        for file in f.readlines():
            base_file = BaseFile(file.strip(), lexer)
            base_files.append(base_file)

    with open(consult_file, 'r', encoding='utf-8') as f:
      text = f.read()
      consult_text = text.strip()

    consult = Consult(consult_text, lexer)
    inverted_index = create_inverted_index(base_files)
    #consult.evaluate(inverted_index)

if __name__ == "__main__":
    main()
