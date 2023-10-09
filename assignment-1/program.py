import nltk
import sys

nltk.download("stopwords")
nltk.download('punkt')
nltk.download("rslp")

class InvertedIndex: 
  def create(self, booleanModel):
    index_file = 'indice.txt'

    # TODO: convert to string builder
    string = ''
    for term, tupls in booleanModel.items():
      string += f"{term}:"
      for tupl in tupls:
        string += f" {str(tupl[0])},{str(tupl[1])}"
      string += "\n"

    with open(index_file, 'w') as f:
      f.write(string)

    return string

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
            "|": "|",
            "&": "&",
            "!": "!",
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
          expr.left = Term(self.lexer.extract_radical(tokens[i + 1]))
        else:
          expr.left = Term(self.lexer.extract_radical(tokens[i - 1]))

        if (ast is None):
          ast = expr
        else:
          lastNode.right = expr
        lastNode = expr

    return ast

  def evaluate(self, ast, boolean_model):
    if (ast is None):
      return set()

    if (isinstance(ast, Term)):
      return self.files_set(boolean_model[ast.value])

    left = self.evaluate(ast.left, boolean_model)
    right = self.evaluate(ast.right, boolean_model)

    print(f"left {left}")
    print(f"right {right}")

    if (ast.kind == self.keywords["&"]):
      return left.union(right)
    if (ast.kind == self.keywords["|"]):
      return left.union(right)
    if (ast.kind == self.keywords["!"]):
      return right - left

  def files_set(self, tuplas):
    files = set()
    for tupl in tuplas:
      files.add(tupl[0])
    return files

  def response(self, boolean_model, base):
    response_file = 'resposta.txt'
    ast = self.generate_ast()

    files = self.evaluate(ast, boolean_model)
    
    string = f"{len(files)}\n"
    for file in files:
      string += f"{base[file - 1].name}\n"

    with open(response_file, 'w') as f:
      f.write(string)

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
    stopwords_list = self.nltk.corpus.stopwords.words("portuguese")+[' ', '.', '..', '...', ',', '!', '?', '\n', '\r\n']
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

    boolean_model = BooleanModel().create(base_files)
    # inverted_index = InvertedIndex().create(boolean_model)
    consult.response(boolean_model, base_files)

if __name__ == "__main__":
    main()
