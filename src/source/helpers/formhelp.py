from wtforms import validators

def tostring(dicti):
    res=""
    for x in dicti:
        res+=x+": "+''.join(dicti[x])+" \n "
    return res

imageext=set(['jpeg','jpg','gif','png','apng','tiff','svg','bmp','ico'])
def imagecheck(form, field):

    ext=field.data.filename.split('.')[-1].lower()
    if ext not in imageext:
        raise validators.ValidationError('Invalid image extension')