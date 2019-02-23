import subprocess
import sys, fileinput
import json
import os
from subprocess import Popen, PIPE

testJustScript = False

# structureRequestAgi = {"taskSelected":{"PHOTO_ALIGN":True},"quality":"high"}
tasksForAgisoftDefault = {
    "taskSelected":{
        'MESH': False, 
        'DENSE_CLOUD': False, 
        'TEXTURE': False, 
        'PHOTO_ALIGN': True, 
        'POLY_DECIMATION': False
    },
    "quality":"low",
    "directoryImages":"/Users/zarfaouik/Desktop/Electron/AGISOFT_TEST/monument"
}
tasksForAgisoft = '{}'

for line in fileinput.input():
    tasksForAgisoft = line
    pass

pathProgram = 'D:/Agisoft/photoscan.exe'
print('SCRIPT 1 - START')
sys.stdout.flush()

currentDir = os.path.dirname(os.path.abspath(__file__))
pathScript = currentDir + '/agisoftScript.py'

tasksForAgisoftDefault = json.dumps(tasksForAgisoftDefault)
args = [pathProgram, '-r', pathScript, tasksForAgisoft]
#subprocess.call(args)

p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
while True:
  line = p.stdout.readline()
  if not line: break
  line = line.decode("utf-8")
  if line.strip():
      print(line)

#output, err = p.communicate(b"input data that is passed to subprocess' stdin")
#rc = p.returncode


print('FINE 1 - START')
sys.stdout.flush()

print('Launcher script agisoft ended.')