import sys
import nltk
import math

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

# doc1: (peso1, peso2, peso3)
# doc2: (peso1, peso2, peso3)
class VectorModel:
  def __init__(self):
    self.idfTerms = {}
    self.tfIdfDocs = {}
    self.termFrequencyByDoc = {}

  def create(self, files):
      self.calculateIdfTerms(files)
      self.calculateTfIdfDocs(files)

  def calculateIdfTerms(self, files):
    docsTermsOccurrences = {}

    for file in files:
      alreadyCount = {}
      for term in file.terms: 
        if (file.name in self.termFrequencyByDoc):
          termsOccurrencesInDoc = self.termFrequencyByDoc[file.name]
          if (term in termsOccurrencesInDoc):
            termsOccurrencesInDoc[term] += 1
          else:
            termsOccurrencesInDoc[term] = 1
        else:
          temp = {term: 1}
          self.termFrequencyByDoc[file.name] = temp

        if (term not in alreadyCount):
          alreadyCount[term] = True
          if (term in docsTermsOccurrences):
            docsTermsOccurrences[term] += 1
          else:
            docsTermsOccurrences[term] = 1
    
    filesQtd = len(files)
    for term in docsTermsOccurrences:
      self.idfTerms[term] = self.calculateIdf(filesQtd, docsTermsOccurrences[term])

  def calculateTfIdfDocs(self, files):
    for file in files:
      temp = []
      terms = self.termFrequencyByDoc[file.name]
      for term in terms:
        if (term in terms):
          tfIdf = self.calculateTfIdf(terms[term], self.idfTerms[term])
          temp.append((term, tfIdf))
          
      self.tfIdfDocs[file.name] = temp

    return

  def calculateSimilarity(self, v1, v2):
    multiplicationSum = 0
    squareSumV1 = 0
    squareSumV2 = 0

    for termWeight2 in v2:
      term = termWeight2[0]
      weight2 = termWeight2[1]
      weight1 = 0

      for termWeight1 in v1:
        if term == termWeight1[0]:
          weight1 = termWeight1[1]
      
      multiplicationSum += (weight1 * weight2)
      squareSumV1 += math.pow(weight1, 2)
      squareSumV2 += math.pow(weight2, 2)
      
    denominator = math.sqrt(squareSumV1) * math.sqrt(squareSumV2)

    return (multiplicationSum / denominator) if denominator > 0 else 0

  def calculateIdf(self, N, Ni):
    return math.log10(N/Ni)

  def calculateTfIdf(self, frequency, idfTerms):
    return (1 + math.log10(frequency)) * idfTerms

class Weights:
  def __init__(self):
    self.file = "pesos.txt"

  def create(self, tfIdfDocs):
    str = ""
    for doc in tfIdfDocs:
      str += doc + ":"
      for weight in tfIdfDocs[doc]:
        if (weight[1] > 0.0):
          str += " " + weight[0] + "," + weight[1].__str__()
      str += "\n"
    return str

# Class to represent each file in the base 
class BaseFile:
  def __init__(self, name, lexer):
    self.name = name
    self.terms = []
    self.lexer = lexer
    self.extract_terms()

  def extract_terms(self):
    alreadyExtractTerms = len(self.terms)
    if (alreadyExtractTerms):
      return
    
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
  def __init__(self, text, lexer, vectorModel):
    self.text = text
    self.keywords = {
      "&": "&",
    }
    self.lexer = lexer
    self.tokens = lexer.tokenize_text(text)
    self.vectorModel = vectorModel

  def vectorWeights(self):
    vector = []
    for term in self.tokens:
      if (term not in self.keywords):
        t = self.lexer.extract_radical(term)
        idf = self.vectorModel.idfTerms[t]
        tfIdf = self.vectorModel.calculateTfIdf(1, idf)
        vector.append((t, tfIdf))

    return vector

  def result(self, vectors):
    consultVector = self.vectorWeights()
    result = []
    for doc in vectors:
      sim = self.vectorModel.calculateSimilarity(consultVector, vectors[doc])
      if sim > 0.001: 
        result.append((doc, sim))
    
    return result

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

class Response:
  def __init__(self):
    self.file = "resposta.txt"

  def build(self, similaritiesArray):
    str = len(similaritiesArray).__str__() + "\n"
    for sim in similaritiesArray:
      str += sim[0].__str__() + " " + sim[1].__str__() + "\n"
    return str

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

  vectorModel = VectorModel()
  vectorModel.create(base_files)
  
  weights = Weights()
  weightsFormatted = weights.create(vectorModel.tfIdfDocs)

  consult = Consult(consult_text, lexer, vectorModel)
  result = consult.result(vectorModel.tfIdfDocs)

  response = Response()
  response_str = response.build(result)

  # # Save files
  storage.write(weights.file, weightsFormatted)
  storage.write(response.file, response_str)

if __name__ == "__main__":
  main()
