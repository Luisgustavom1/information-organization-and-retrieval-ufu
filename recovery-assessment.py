import sys
import math
import numpy as np
import matplotlib.pyplot as plt

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
    self.numberOfConsultations = 0
    self.metricsService = metricsService
    # (consult1[], {reference1: reference1}), (consult2[], {reference2: reference2}), (consult3[], {reference3: reference3})
    self.consultationReferenceTuples = []
  
  def extractConsults(self):
    self.numberOfConsultations = int(self.referenceTextList[0].strip())

    for index in range(1, self.numberOfConsultations + 1):
      referenceMap = {}
      for reference in self.referenceTextList[index].split(' '):
        referenceMap[reference] = reference

      tupl = (self.referenceTextList[index + self.numberOfConsultations].split(' '), referenceMap)
      self.consultationReferenceTuples.append(tupl)

  def calculatePrecisions(self):
    systemPrecisions = []
    
    for consultationReferenceTupl in self.consultationReferenceTuples:
      systemPrecisions.append(
        self.metricsService.calculatePrecisions(
          self.metricsService.calculate(consultationReferenceTupl)
        )
      )

    return systemPrecisions

  def calculatePrecisionsMedia(self, systemPrecisions):
    return self.metricsService.calculateMedia(systemPrecisions)

class Metrics:
  def __init__(self):
    self.revocations = [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1]

  def calculate(self, consultationReferenceTupl):
    # [allRevocations, allPrecisions]
    revocationPrecisionMatrix = [[], []]
    consult = consultationReferenceTupl[0]
    reference = consultationReferenceTupl[1]

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
    systemPrecisions = metric[1]
    
    # greater precision in revocations greater than or equal to rJ
    for revocation in self.revocations:
      candidatePrecisions = []
      for index in range(len(consultRevocations)):
        if consultRevocations[index] >= revocation:
          candidatePrecisions.append(systemPrecisions[index])

      revocationPrecisionMap[revocation] = np.array(candidatePrecisions).max() if len(candidatePrecisions) > 0 else 0
    
    return revocationPrecisionMap

  def calculateMedia(self, systemPrecisions):
    result = {}
    for revocation in self.revocations:
      sum = 0
      for revocationPrecisionMap in systemPrecisions:
        sum += revocationPrecisionMap[revocation]
      result[revocation] = sum / len(systemPrecisions)

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
  systemPrecisions = references.calculatePrecisions()
  precisionMedia = references.calculatePrecisionsMedia(systemPrecisions)

  response = Response()
  storage = Storage()
  # # Save files
  storage.write(response.file, response.build(precisionMedia))

  for index, systemPrecision in enumerate(systemPrecisions):
    x = systemPrecision.values()
    y = systemPrecision.keys()

    plt.title('Consulta de referência ' + (index + 1).__str__())
    plt.plot(x, y, '-o')  # a opção '-o' é para colocar um círculo sobre os pontos e liga-los por segmentos de reta
    plt.show()

  x = precisionMedia.values()
  y = precisionMedia.keys()

  plt.title('Média')
  plt.plot(x, y, '-o')  # a opção '-o' é para colocar um círculo sobre os pontos e liga-los por segmentos de reta
  plt.show()


if __name__ == "__main__":
  main()
