import sys
import math
import numpy as np
import matplotlib as mpl

# Class responsible for storage
class Storage:
  def write(self, file, content):
    with open(file, "w") as f:
      f.write(content)

class Response:
  def __init__(self):
    self.file = "media.txt"

  def build(self, mediaMap):
    str = ""
    for media in mediaMap.values():
      str += (np.around(media, decimals=2).__str__() if media > 0 else "0") + " "
    return str

class References:
  def __init__(self, referenceTextList, metricsService):
    self.referenceTextList = referenceTextList
    self.numberOfConsults = 0
    self.metricsService = metricsService
    # (consult1[], {reference1: reference1}), (consult2[], {reference2: reference2}), (consult3[], {reference3: reference3})
    self.consultReferenceTuples = []
  
  def extractConsults(self):
    self.numberOfConsults = int(self.referenceTextList[0].strip())

    for index in range(1, self.numberOfConsults + 1):
      referenceMap = {}
      for reference in self.referenceTextList[index].split(' '):
        referenceMap[reference] = reference

      tupl = (self.referenceTextList[index + self.numberOfConsults].split(' '), referenceMap)
      self.consultReferenceTuples.append(tupl)

  def calculatePrecisionsMedia(self):
    consultPrecisions = []

    for consultReferenceTupl in self.consultReferenceTuples:
      consultPrecisions.append(
        self.metricsService.calculatePrecisions(
          self.metricsService.calculate(consultReferenceTupl)
        )
      )

    return self.metricsService.calculateMedia(consultPrecisions)

class Metrics:
  def __init__(self):
    self.revocations = [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1]

  def calculate(self, consultReferenceTupl):
    # [allRevocations, allPrecisions]
    revocationPrecisionMatrix = [[], []]
    consult = consultReferenceTupl[0]
    reference = consultReferenceTupl[1]

    relevantDocsFound = 0

    for index in range(len(consult)):
      if (consult[index] in reference):
        relevantDocsFound += 1
        revocation = relevantDocsFound / len(reference)
        precision = relevantDocsFound / (index + 1)

        revocationPrecisionMatrix[0].append(revocation)
        revocationPrecisionMatrix[1].append(precision)

    return revocationPrecisionMatrix

  def calculatePrecisions(self, metric):
    revocationPrecisionMap = {}
    consultRevocations = metric[0]
    consultPrecisions = metric[1]
    
    # greater precision in revocations greater than or equal to rJ
    for revocation in self.revocations:
      candidatePrecisions = []
      for index in range(len(consultRevocations)):
        if consultRevocations[index] >= revocation:
          candidatePrecisions.append(consultPrecisions[index])

      revocationPrecisionMap[revocation] = np.array(candidatePrecisions).max() if len(candidatePrecisions) > 0 else 0
    
    return revocationPrecisionMap

  def calculateMedia(self, consultPrecisions):
    result = {}
    for revocation in self.revocations:
      sum = 0
      for revocationPrecisionMap in consultPrecisions:
        sum += revocationPrecisionMap[revocation]
      result[revocation] = sum / len(consultPrecisions)

    return result

def main():
  if len(sys.argv) != 2:
      print("Usage: modelo_booleano.py <referencesTxt>")
      sys.exit(1)

  referencesTxt = sys.argv[1]
  
  referencesText = ""
  with open(referencesTxt, "r") as f:
    referencesText = f.read()

  references = References(referencesText.split('\n'), Metrics())
  references.extractConsults()
  precisionMedia = references.calculatePrecisionsMedia()

  response = Response()
  
  storage = Storage()
  # # Save files
  storage.write(response.file, response.build(precisionMedia))
  # storage.write(response.file, response_str)

if __name__ == "__main__":
  main()
