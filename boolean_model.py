import sys
import nltk

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("rslp")
nltk.download("mac_morpho")

# Class responsible for storage
class Storage:
  def write(self, file, content):
    with open(file, "w") as f:
      f.write(content)

# Class to generate response
class Response:
  def __init__(self, file_name="resposta.txt"):
    self.file = file_name

  def build(self, files, base):
    response_str = f"{len(files)}\n"
    for file in files:
      response_str += f"{base[file - 1].name}\n"
    return response_str

# Class to build inverted index from the boolean model
class InvertedIndex:
  def __init__(self, file_name="indice.txt"):
    self.file = file_name

  def build(self, boolean_model):
    # TODO: convert to string builder
    inverted_index_str = ""
    for term, tupls in boolean_model.items():
      inverted_index_str += f"{term}:"
      for tupl in tupls:
        inverted_index_str += f" {str(tupl[0])},{str(tupl[1])}"
      inverted_index_str += "\n"

    return inverted_index_str

class BooleanModel:
  def create(self, files):
      boolean_model = {}

      for i, file in enumerate(files):
        file_index = self.get_occurrences(file)
        for key, value in file_index.items():
            tupl = (i + 1, value)
            boolean_model.setdefault(key, []).append(tupl)

      return boolean_model

  def get_occurrences(self, file):
    file.extract_terms()
    boolean_model = {}

    for term in file.terms:
      if (term in boolean_model):
        boolean_model[term] += 1
      else:
        boolean_model[term] = 1

    return boolean_model

# Class to represent each file in the base 
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

# Classes to build lexer, parser and interpreter the consult
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
      self.index += 1
      if token in self.keywords:
        left = Expr(token, left, self.parse_term())
      else:
        # TODO: not get position by index, add metadata to tokens
        raise SyntaxError(f"unexpected token in position: {self.index}, received: {token}")
    return left

  def parse_term(self):
    token = self.tokens[self.index]
    self.index += 1
    if token == self.keywords['!']:
      return Expr(token, None, self.parse_term())
    if token.isalpha():
      return Term(self.lexer.extract_radical(token))
    raise SyntaxError("unexpected token")

  def evaluate(self, ast, boolean_model, base):
    if ast is None:
      return set()
    if isinstance(ast, Term):
      return self.files_set(boolean_model[ast.value])
    left = self.evaluate(ast.left, boolean_model, base)
    right = self.evaluate(ast.right, boolean_model, base)
    if ast.kind == self.keywords["&"]:
      return left & right
    if ast.kind == self.keywords["|"]:
      return left | right
    if ast.kind == self.keywords["!"]:
      all_base = set(range(1, len(base) + 1))
      return all_base - right

  def files_set(self, tuplas):
    return {tupl[0] for tupl in tuplas}

  def response(self, boolean_model, base):
    ast = self.generate_ast()
    files = self.evaluate(ast, boolean_model, base)
    return files

class TextLexer:
  def __init__(self, nltk):
    self.nltk = nltk

  def extract_radical(self, term):
    extrator = self.nltk.stem.RSLPStemmer()
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
      print("Usage: modelo_booleano.py <baseTxt> <consultTxt>")
      sys.exit(1)

  baseTxt = sys.argv[1]
  consultTxt = sys.argv[2]

  lexer = TextLexer(nltk)
  storage = Storage()

  base_files = []

  with open(baseTxt, "r", encoding="utf-8") as f:
    for file in f.readlines():
      base_file = BaseFile(file.strip(), lexer)
      base_files.append(base_file)

  with open(consultTxt, "r", encoding="utf-8") as f:
    text = f.read()
    consult_text = text.strip()

  boolean_model = BooleanModel().create(base_files)

  consult = Consult(consult_text, lexer)
  result_files = consult.response(boolean_model, base_files)

  inverted_index = InvertedIndex()
  inverted_index_str = inverted_index.build(boolean_model)

  response = Response()
  response_str = response.build(result_files, base_files)

  # Save files
  storage.write(inverted_index.file, inverted_index_str)
  storage.write(response.file, response_str)

if __name__ == "__main__":
  main()
