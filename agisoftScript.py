import os
import PhotoScan
import json
import sys
import time

print('SCRIPT 1 - START')

mapOfOperation = {'MESH': True, 'DENSE_CLOUD': True, 'TEXTURE': True, 'PHOTO_ALIGN': True, 'POLY_DECIMATION': False}
requestAgisoft=json.loads(sys.argv[1]) 

print('----------------- taskSelected & quality ----------')
print(requestAgisoft)
# INPUT PARAMETETRI
taskSelected = requestAgisoft['taskSelected']
mapOfOperation = taskSelected

if(mapOfOperation == {}):
    print('MapOp: ',mapOfOperation)
    sys.exit()

quality = requestAgisoft['quality']
print(quality)

path_photos = requestAgisoft['directoryImages']
print(path_photos)

filenameProject = 'projectAgisoft-1'
print(filenameProject)

# CONSTANT
CURRENT_OPERATION = ""
percentDecimateModel = 15 / 100 # Decimate model percentual

 
PhotoAlignmentQ = PhotoScan.LowAccuracy #Photo alignment | Quality low --> PhotoScan.HighAccuracy
BuildDepthMapsQ = PhotoScan.LowestQuality #Dense cloud | Quality low --> PhotoScan.HighQuality
MeshFaceCountQuality = PhotoScan.FaceCount.LowFaceCount #Mesh Quality --> PhotoScan.FaceCount.MediumFaceCount

if quality == 'high': 
    PhotoAlignmentQ = PhotoScan.HighestAccuracy #Photo alignment Quality 
    BuildDepthMapsQ = PhotoScan.UltraQuality #Dense cloud Quality
    MeshFaceCountQuality = PhotoScan.FaceCount.HighFaceCount #Mesh Quality 


def getEsito(currentOperation, msg, code):
        esito = {"currentOperation": currentOperation ,"msgEsito": msg, "codeEsito": code}
        return json.dumps(esito)

def progress_print(p):
        print('Current task name:' + CURRENT_OPERATION)
        print('Current task progress: {:.2f}%'.format(p))
        sys.stdout.flush()

def progress_print_json(p):
        obj = {"taskName": CURRENT_OPERATION, "taskProgress": p}
        print(json.dumps(obj))
        sys.stdout.flush()

def align(chunk):
        # Processing:
        CURRENT_OPERATION = "Photo alignment"
        chunk.matchPhotos(accuracy=PhotoScan.LowAccuracy, generic_preselection=True,
                        reference_preselection=False, progress=progress_print_json)
        chunk.alignCameras()

        CURRENT_OPERATION = "Build depth maps"
        chunk.buildDepthMaps(quality=PhotoScan.LowestQuality,
                            filter=PhotoScan.AggressiveFiltering, progress=progress_print_json)

def getChunkByLabel(doc, label):
        for tmpChunk in doc.chunks:
            print(tmpChunk.label)
            if tmpChunk.label == label:
                return tmpChunk

def getListPhotoDir(pathDir):
        image_list = os.listdir(pathDir)
        photo_list = list()

        for photo in image_list:
            if photo.rsplit(".", 1)[1].lower() in ["jpg", "jpeg", "tif", "tiff"]:
                photo_list.append("/".join([pathDir, photo]))
        
        return photo_list

def lockFile(pathDir):
        if os.path.exists( pathDir + '/test1.files/lock' ):
            os.remove( pathDir + '/test1.files/lock' )

def taskIsEnable(task, mapTasks):
    return (task in mapTasks) and mapTasks[task]

try:
    print('sdsa')
    doc = PhotoScan.app.document
    doc = PhotoScan.app.document
    chunk = doc.addChunk()
    chunk.label = "MyChunk"

    
    # AGGIUNGO LE FOTO AL CHUNK
    list_photo = getListPhotoDir(path_photos)
    chunk.addPhotos(list_photo)

    #PHOTO ALIGNMENT
    CURRENT_OPERATION = "Photo alignment"
    chunk.matchPhotos(accuracy=PhotoScan.LowAccuracy, generic_preselection=True,
                        reference_preselection=False, progress=progress_print_json)
    chunk.alignCameras()
    

    #DENSE CLOUD
    if taskIsEnable('DENSE_CLOUD', mapOfOperation): 
        CURRENT_OPERATION = "Dense cloud"
        chunk.buildDepthMaps(quality=PhotoScan.LowestQuality,filter=PhotoScan.AggressiveFiltering, progress=progress_print_json)
        a = chunk.buildDenseCloud(progress=progress_print_json)
        print(a)

    # MESH --> recupera facce
    if taskIsEnable('MESH', mapOfOperation):
        CURRENT_OPERATION = "Mesh"
        a = chunk.buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation,face_count=MeshFaceCountQuality, progress=progress_print_json)

    # DECIMATE MESH
    if taskIsEnable('POLY_DECIMATION', mapOfOperation):
        CURRENT_OPERATION = "Decimate model"
        statistics = chunk.model.statistics()
        #Rimuovo un 15%
        decimate_face = statistics.faces - (statistics.faces * percentDecimateModel)
        decimate_face = round(decimate_face)
        print(statistics.faces, ' ', decimate_face)
        tmp = chunk.decimateModel(face_count=decimate_face, progress=progress_print)
        statistics = chunk.model.statistics()
        print(statistics.faces, ' ', decimate_face)

    # TEXTURE
    if taskIsEnable('TEXTURE', mapOfOperation):
        CURRENT_OPERATION = "Texture"
        chunk.buildUV(mapping=PhotoScan.GenericMapping)
        chunk.buildTexture(blending=PhotoScan.MosaicBlending, size=4096, progress=progress_print_json)


    CURRENT_OPERATION = "Salvataggio"
    print("Salvataggio in corso")

    doc.save(path_photos + "/" + filenameProject + ".psx")
        
    print(getEsito(CURRENT_OPERATION, path_photos + "/" + filenameProject + ".psx", 0))

     # /Applications/PhotoScanPro.app/Contents/MacOS/PhotoScanPro -r /Users/zarfaouik/Desktop/Electron/angular-electron/scripts/script1.py
except:
    print('current op: ', CURRENT_OPERATION)
    print(getEsito(CURRENT_OPERATION, "Errore", -1))
