from gimpfu import *

temp_name = 'Latex TEMP'

def top_layer_is_TEMP(img, ind=0):
    return bool(img.layers[ind].name.find(temp_name) == 0)


def top_layer_is_Latex(img, ind=0, name='Latex'):
    return bool(img.layers[ind].name.find(name) == 0)


def scale_image(img, max_w, max_h, debug=0):
    if debug:
        print('max_w = '+str(max_w))
        print('max_h = '+str(max_h))
        print('img.width = '+str(img.width))
        print('img.height = '+str(img.height))
    if (img.width > max_w) or (img.height > max_h):
        s1 = float(img.width)/float(max_w)
        s2 = float(img.height)/float(max_h)
        ar = float(img.height)/float(img.width)
        if s1 > s2:
            if debug:
                print('using max_w')
            new_w = max_w
            new_h = max_w*ar
        else:
            if debug:
                print('using max_h')
            #Pdb.set_trace()
            new_h = max_h
            new_w = max_h/ar
        pdb.gimp_image_scale(img, new_w, new_h)
    return img


def copy_img2_to_img(img2, img, x_offset=None, y_offset=None, \
                     autocrop=True):
    if autocrop:
        pdb.plug_in_autocrop(img2, img2.layers[0])
    w = img.width
    max_w = w-50
    h = img.height
    max_h = h-50
    if x_offset is not None:
        max_w -= x_offset
    if y_offset is not None:
        max_h -= y_offset
    scale_image(img2, max_w, max_h)
    pdb.gimp_edit_copy_visible(img2)
    #gimp.Display(img2)
    width = img.width
    height = img.height
    #print('width = %s' % width)
    #print('height = %s' % height)
    if top_layer_is_TEMP(img):
        trans_layer = img.layers[0]
    else:
        trans_layer = gimp.Layer(img, 'Latex', width, height, \
                                 RGBA_IMAGE, 100, NORMAL_MODE)
        img.add_layer(trans_layer)
    float_layer = pdb.gimp_edit_paste(trans_layer, 1)
    if (x_offset is not None) or (y_offset is not None):
        if x_offset is None:#if either is not None, the other defaults
            #to 0
            x_offset = 0
        if y_offset is None:
            y_offset = 0
        pdb.gimp_layer_set_offsets(float_layer, x_offset, y_offset)
    else:
        mcmd = "xdotool key M"
        time.sleep(0.1)
        os.system(mcmd)
    pdb.gimp_image_delete(img2)
    return float_layer


def copy_pdf_to_img(pdf_path, img, x_offset=None, y_offset=None, \
                    autocrop=True):
    img2 = pdb.file_pdf_load(pdf_path, pdf_path)
    return copy_img2_to_img(img2, img, x_offset=x_offset, y_offset=y_offset, \
                            autocrop=autocrop)

def copy_jpg_to_img(jpg_path, img, x_offset=None, y_offset=None, \
                    autocrop=True):
    img2 = pdb.gimp_file_load(jpg_path, jpg_path)
    return copy_img2_to_img(img2, img, x_offset=x_offset, y_offset=y_offset, \
                            autocrop=autocrop)


def copy_png_to_img(png_path, img, x_offset=None, y_offset=None, \
                    autocrop=True):
    img2 = pdb.gimp_file_load(png_path, png_path)
    return copy_img2_to_img(img2, img, x_offset=x_offset, y_offset=y_offset, \
                            autocrop=autocrop)

