
from fileinput import filename
from itertools import count
from math import floor
# from xml.etree.ElementPath import xpath_tokenizer
from PIL import Image
from math import *
import os
from matplotlib import image
# -*- coding: utf-8 -*-
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM


test_image = "roadTexture_02.png"


def get_isometric(image_path, isometricBackgroundColor=None):
    os.makedirs("assets/temp_isometric/", exist_ok=True)  # succeeds even if directory exists.
    temp_folder_name = "assets/temp_isometric/"

    if image_path[-3:] != 'png':
        return


    txr = Image.open(image_path)
    txr = txr.convert('RGB')
    txrp = txr.load()

    angle = 60
    angle_rad = 2 * pi * angle /360 

    y_pix = cos(angle_rad)
    x_pix = sin(angle_rad)

    txs=txr.width
    tys=txr.height

    sxs = ceil(txs + txs*x_pix)
    sys = ceil(tys + tys*y_pix)
    height=0.02*sys;  

    spr = Image.new("RGB", (sxs, sys), (10, 50, 10))
    sprp = spr.load()
    
    sprp[0, 0] = (200, 200, 3)

    # [render sprite]
    th= height # height of tile in texture [pixels]

    
    x0=0; y0=(txs*y_pix)

    for i in range(txr.width):
        for j in range(txr.height):
            xx = x0 + (i + j) * x_pix
            yy = y0 + (j-i) * y_pix

            if (xx>=0) and (xx<sxs) and (yy>=0) and (yy<sys):
                sprp[xx, yy]=txrp[i, j]

    # left side
    x0l=0; y0l=(txs*y_pix)
    for i in range(txr.width):
        if i < th:
            for j in range(txr.height):
                xxl=floor(x0l+(j      )*x_pix)
                yyl=floor(y0l+(j+(2*i))*y_pix)

                if ((xxl>=0) and (xxl<sxs) and (yyl>=0) and (yyl<sys)):
                    sprp[xxl, yyl]=txrp[i, j]

    # right side
    x0=txs*x_pix; y0=(tys*y_pix + txs*y_pix )
    print(y0)
    for i in range(tys):
        if i < th:

            for j in range(txs):
                xx=x0+(+j      )*x_pix
                yy=y0+(-j+(2*i))*y_pix

                if ((xx>=0) and (xx<sxs) and (yy>=0) and(yy<sys)):
                    sprp[xx, yy]=txrp[i, j]
                    # if xx < txs and yy < tys:
                    #     print(txrp[xx, yy])

    filename = 'assets/temp_isometric/temp.png'
    spr.save(filename)
    spr.show()
    return filename