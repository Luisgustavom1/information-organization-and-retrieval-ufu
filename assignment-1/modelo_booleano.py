import nltk
import sys

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("rslp")
nltk.download("mac_morpho")

class InvertedIndex: 
  def create(self, booleanModel):
    index_file = "indice.txt"

    # TODO: convert to string builder
    string = ""
    for term, tupls in booleanModel.items():
      string += f"{term}:"
      for tupl in tupls:
        string += f" {str(tupl[0])},{str(tupl[1])}"
      string += "\n"

    with open(index_file, "w") as f:
      f.write(string)

      return string

class BooleanModel:
  def create(self, files):
      boolean_model = {}

      for i, file in enumerate(files):
        file_index = self.generate_boolean_model(file)
        for key, value in file_index.items():
            tupl = (i + 1, value)
            if (key in boolean_model):
              boolean_model[key].append(tupl)
            else:
              boolean_model[key] = [tupl]

      return boolean_model

  def generate_boolean_model(self, file):
    file.extract_terms()
    boolean_model = {}

    for term in file.terms:
      if (term in boolean_model):
        boolean_model[term] += 1
      else:
        boolean_model[term] = 1

    return boolean_model

class Term:
    def __init__(self, value):
        self.value = value

class Expr:
    def __init__(self, kind, left=None, right=None):
        self.kind = kind
        self.left = left
        self.right = right

class Consult:
  def __init__(self, text, lexer):
        self.text = text
        self.keywords = {
            "|": "|",
            "&": "&",
            "!": "!",
        }
        self.tokens = lexer.tokenize_text(text)
        self.lexer = lexer
        self.index = 0

  def generate_ast(self):
      left = self.parse_term()

      while self.index < len(self.tokens):
          token = self.tokens[self.index]

          if token == self.keywords["!"]:
              self.index += 1
              right = self.parse_term()
              left = Expr(self.keywords["!"], left, right)
          elif token in (self.keywords["&"], self.keywords["|"]):
              kind = token
              self.index += 1
              right = self.parse_term()
              left = Expr(kind, left, right)
          else:
              raise SyntaxError("Operador inválido")

      return left

  def parse_term(self):
      if self.index >= len(self.tokens):
          return None

      token = self.tokens[self.index]
      self.index += 1

      if token == self.keywords['!']:
          return Expr(self.keywords['!'], None, self.parse_term())
      elif token.isalpha():
          return Term(self.lexer.extract_radical(token))
      else:
          raise SyntaxError("Token inválido")

  def print_ast(self, a, indent=""):
    if isinstance(a, Term):
        print(indent + "Term: " + a.value)
    elif isinstance(a, Expr):
        print(indent + "Expr: " + a.kind)
        if a.left:
            self.print_ast(a.left, indent + "  ")
        if a.right:
            self.print_ast(a.right, indent + "  ")

  def evaluate(self, ast, boolean_model, base):
    if (ast is None):
      return set()

    if (isinstance(ast, Term)):
      return self.files_set(boolean_model[ast.value])

    if (ast.kind == self.keywords["!"]):
      all_docs = set(range(1, len(base) + 1))
      right = self.evaluate(ast.right, boolean_model, base)
      return all_docs - right
    if (ast.kind == self.keywords["&"]):
      left = self.evaluate(ast.left, boolean_model, base)
      right = self.evaluate(ast.right, boolean_model, base)
      return left.intersection(right)
    if (ast.kind == self.keywords["|"]):
      left = self.evaluate(ast.left, boolean_model, base)
      right = self.evaluate(ast.right, boolean_model, base)
      return left.union(right)

    return ast.value in boolean_model

  def files_set(self, tuplas):
    files = set()
    for tupl in tuplas:
      files.add(tupl[0])
    return files

  def response(self, boolean_model, base):
    response_file = "resposta.txt"
    ast = self.generate_ast()

    # self.print_ast(ast)
    print(f"     {ast.kind}")
    print(f"   {ast.left.kind}    {ast.right.kind}")
    print(f"{ast.left.left.value} {ast.left.right.kind}    - {ast.right.right.value}")
    print(f"- - {ast.left.right.right.value} -    - -")
    # set(range(1, len(base) + 1))
    files = self.evaluate(ast, boolean_model, base)
    print(files)
    string = f"{len(files)}\n"
    for file in files:
      string += f"{base[file - 1].name}\n"

    with open(response_file, "w") as f:
      f.write(string)

class BaseFile:
  def __init__(self, name, lexer):
        self.name = name
        self.terms = []
        self.lexer = lexer

  def extract_terms(self):
    with open(self.name, "r", encoding="utf-8") as f:
      text = f.read()
      tokens = self.extract_tokens(text)
      self.terms = self.remove_stopwords(tokens)
      self.terms.sort()

  def extract_tokens(self, text):
    return self.lexer.tokenize_text(text)

  def remove_stopwords(self, tokens):
    stopwords = self.lexer.get_stopwords()
    clean_tokens = []

    for token in tokens:
      if (not token in stopwords):
        clean_tokens.append(self.lexer.extract_radical(token))

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
    stopwords_list = self.nltk.corpus.stopwords.words("portuguese")+[" ", ".", "..", "...", ",", "!", "?", "\n", "\r\n", "daqui", "enquanto", "porque", "pra", "embora", "pois", "sobre"]
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

    with open(base, "r", encoding="utf-8") as f:
        for file in f.readlines():
            base_file = BaseFile(file.strip(), lexer)
            base_files.append(base_file)

    with open(consult_file, "r", encoding="utf-8") as f:
      text = f.read()
      consult_text = text.strip()

    consult = Consult(consult_text, lexer)

    boolean_model = BooleanModel().create(base_files)
    inverted_index = InvertedIndex().create(boolean_model)
    consult.response(boolean_model, base_files)

if __name__ == "__main__":
    main()