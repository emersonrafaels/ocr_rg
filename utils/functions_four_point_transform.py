import cv2
import os
import pytesseract
from PIL import Image

path = os.getcwd()

caminho_imagem = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\2.jpg'


image = cv2.imread(caminho_imagem)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5,5), 0)
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Remove dotted lines
cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    area = cv2.contourArea(c)
    if area < 5000:
        cv2.drawContours(thresh, [c], -1, (0,0,0), -1)

# Fill contours
close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
close = 255 - cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, close_kernel, iterations=6)
cnts = cv2.findContours(close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    area = cv2.contourArea(c)
    if area < 15000:
        cv2.drawContours(close, [c], -1, (0,0,0), -1)

# Smooth contours
close = 255 - close
open_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20,20))
opening = cv2.morphologyEx(close, cv2.MORPH_OPEN, open_kernel, iterations=3)

# Busca los contornos y dibuja los resultados
ROI_number = 0
cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    cv2.drawContours(image, [c], -1, (36,255,12), 3)
    #aqui se realiza el recorte de cada entidad
    x,y,w,h = cv2.boundingRect(c)
    ROI = image[y:y+h, x:x+w]
    cv2.imwrite(os.path.join(path , 'imagen_{}.png'.format(ROI_number)), ROI)
    cv2.rectangle(image,(x,y),(x+w,y+h),(36,255,12),2)
    ROI_number += 1


#formo una lista con las imagenes de la ultima carpeta creada
listadeimagenes = os.listdir(path)
print(listadeimagenes)

nuevo = str(path + "1").zfill(7)

print("Cantidad de entidades ", len(cnts))
cv2.imshow('thresh', thresh)
cv2.imshow('opening', opening)
cv2.imshow('image', image)
cv2.waitKey()