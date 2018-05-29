from base64 import b64encode
from PIL import Image
from os import path,remove

def savepic(file,pid,target):
    fn = file.filename.split(".")
    picname = "p" + str(pid) + "." + fn[1]
    destination = "/".join([target, picname])
    file.save(destination)

    siz = 192, 192
    outfile = path.splitext(destination)[0] + ".thumbnail"
    im = Image.open(destination)
    im.thumbnail(siz)
    im.save(outfile, "JPEG")

def deletepic(destination):
    remove(destination)
    remove(path.splitext(destination)[0] + ".thumbnail")

def getthumbnail(pid,target):
    picname = "p" + str(pid) + ".thumbnail"
    destination = "/".join([target, picname])
    image = open(destination, 'rb')
    image_read = image.read()
    image_64_encode =b64encode(image_read)
    encoded=image_64_encode.decode('utf-8')
    return encoded
