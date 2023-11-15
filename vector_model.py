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
    numberOfDocumentsWithTerm = {}

    for file in files:
      alreadyCountTerm = {}
      self.termFrequencyByDoc[file.name] = {}
      for term in file.terms: 
        termsOccurrencesInDoc = self.termFrequencyByDoc[file.name]
        termsOccurrencesInDoc[term] = termsOccurrencesInDoc.get(term, 0) + 1

        if (term not in alreadyCountTerm):
          alreadyCountTerm[term] = True
          numberOfDocumentsWithTerm[term] = numberOfDocumentsWithTerm.get(term, 0) + 1
      
    filesQtd = len(files)
    for term in numberOfDocumentsWithTerm:
      self.idfTerms[term] = self.calculateIdf(filesQtd, numberOfDocumentsWithTerm[term])
    
  def calculateTfIdfDocs(self, files):
    for file in files:
      temp = []
      terms = self.termFrequencyByDoc[file.name]
      for term in terms:
        tfIdf = self.calculateTfIdf(terms[term], self.idfTerms[term])
        temp.append((term, tfIdf))
          
      self.tfIdfDocs[file.name] = temp

    return

  def calculateSimilarity(self, consultVector, docVector):
    multiplicationSum = 0
    squareSumConsultVector = 0
    squareSumDocVector = 0
  
    for vectorTuple in docVector:
      squareSumDocVector += math.pow(vectorTuple[1], 2)
      
    for consultTuple in consultVector:
      term = consultTuple[0]
      weight = consultTuple[1]
      squareSumConsultVector += math.pow(weight, 2)
      for docTuple in docVector:
        if docTuple[0] == term:
          multiplicationSum += weight * docTuple[1]

    denominator = math.sqrt(squareSumConsultVector) * math.sqrt(squareSumDocVector)

    return (multiplicationSum / denominator) if denominator > 0 else 0

  def calculateIdf(self, N, Ni):
    return math.log10(N/Ni)

  def calculateTfIdf(self, frequency, idfTerms):
    return (1 + math.log10(frequency)) * idfTerms if frequency >= 1 else 0

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
    tokensFrequency = {}

    for term in self.tokens:
      if (term not in self.keywords):
        t = self.lexer.extract_radical(term)
        tokensFrequency[t] = tokensFrequency.get(t, 0) + 1

    for term in tokensFrequency:
      idf = self.vectorModel.idfTerms.get(term, 0)
      tfIdf = self.vectorModel.calculateTfIdf(tokensFrequency[term], idf)
      vector.append((term, tfIdf))

    return vector

  def result(self, vectors):
    consultVector = self.vectorWeights()
    result = []
    for doc in vectors:
      sim = self.vectorModel.calculateSimilarity(consultVector, vectors[doc])
      if sim >= 0.001: 
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
    stopwords_list = self.nltk.corpus.stopwords.words("portuguese")+[" ", ".", "..", "...", ",", "!", "?", "\n", "\r\n"]
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
  response_str = response.build(sorted(result, reverse=True, key=lambda tupl: tupl[1]))

  # # Save files
  storage.write(weights.file, weightsFormatted)
  storage.write(response.file, response_str)

if __name__ == "__main__":
  main()
