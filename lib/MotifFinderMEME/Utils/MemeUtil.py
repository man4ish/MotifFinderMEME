import sys
import os
import json
import subprocess

class MemeUtil:
  def __init__(self):
      pass

  def build_meme_command(self, inputFilePath,min,max,background):
      outputFlag = ' -o /kb/module/work/tmp/meme_out -revcomp -dna -nmotifs 10 -minw ' + str(min)+ ' -maxw ' + str(max)
      #no cache
      if background == 1:
          outputFlag += ' -bfile /kb/module/work/tmp/background.txt'
      command = '/kb/deployment/bin/meme/bin/meme '  + inputFilePath + outputFlag
      return command

  def run_meme_command(self, command):
      try:
          meme_out_txt = subprocess.check_output(command,shell=True, stderr=subprocess.STDOUT)
          #print('************PRINTING MEME************\n'+meme_out_txt)
      except subprocess.CalledProcessError as e:
          print('************MEME ERROR************\n')
          print(e.returncode)

  def write_obj_ref(self, path, obj_ref):
      file = open(path+"/meme_obj.txt","w")
      file.write(obj_ref)
      file.close()

  def parse_meme_output(self):
      outputDir = '/kb/module/work/tmp/meme_out'
      outputFile = outputDir + '/meme.txt'
      file = open(outputFile,'r')

      starCount = 0
      countStars = False
      readMotif = False
      processMotif = False
      findLocs = 0
      findPWM = 0
      motifDict = {}
      motifList = []
      for line in file:
          print(line)
          if 'COMMAND LINE SUMMARY' in line:
              countStars = True
              continue
          if 'SUMMARY OF MOTIFS' in line:
              break
          if countStars:
              if '*****************************************************************' in line:
                  starCount += 1
          if starCount != 0 and starCount%3 == 0 and not readMotif:
              #new motif
              if starCount != 3:
                  motifList.append(motifDict)
                  motifDict = {}
                  #add the motif we finished

              readMotif = True
              continue
          if readMotif is True:
              elems = line.replace('\n','').split()
              #print(line)
              motifSignature = elems[1]
              motifDict['Iupac_signature'] = motifSignature
              eval = float(elems[-1])

              motifDict['p-value'] = eval
              motifDict['Locations'] = []
              motifDict['pwm'] = []
              readMotif = False
              processMotif = True
              continue
          if processMotif is True:
              if 'sites sorted by' in line:
                  findLocs = 1
                  continue
              if findLocs == 4:
                  if '-----------------------------' in line:
                      findLocs = 0
                      continue
                  elems = line.replace('\n','').split()
                  #strand id = elems[0]
                  locList = []
                  locList.append(elems[0])
                  locList.append(elems[2])
                  if elems[1] == '+':
                      end = str(int(elems[2])+len(motifSignature))
                  else:
                      end = str(int(elems[2])-len(motifSignature))
                  locList.append(end)
                  locList.append(elems[1])
                  motifDict['Locations'].append(locList)
                  continue
              if findLocs != 0:
                  findLocs += 1
                  continue
              if 'letter-probability matrix' in line:
                  findPWM = 1
                  continue
              if findPWM == 1:
                  if '--------' in line:
                      findPWM = 0
                      continue
                  elems = line.replace('\n','').split()
                  rowList = []
                  rowList.append(('A',float(elems[0])))
                  rowList.append(('C',float(elems[1])))
                  rowList.append(('G',float(elems[2])))
                  rowList.append(('T',float(elems[3])))
                  motifDict['pwm'].append(rowList)
      jsonFilePath = outputDir + '/meme.json'
      with open(jsonFilePath,'w') as jsonFile:
          json.dump(motifList,jsonFile)
      return motifList
