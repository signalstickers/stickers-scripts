import apng
import struct
import sys
from PIL import Image
from io import BytesIO


# How to use:
# import this file, and give to resize() an APNG image in bytes




# Change this color if there is pure green in the images
#
# TODO choose a random color and make sure it is not present in the image
ALPHA_COLOR = (0, 255, 0)


def p_to_rgba(img):

    palette = img.palette.tobytes()
    fmt = "c" * len(palette)
    struct_list = list(struct.unpack(fmt, palette))
    all_rbg = [int.from_bytes(i, byteorder='big') for i in struct_list]

    for i, j in enumerate(range(0, len(all_rbg), 3)):
        color_rgb = tuple(all_rbg[j:j + 3])
        if color_rgb == ALPHA_COLOR:
            index_alpha = i
            break

    try:
        # Set the `index_alpha`th entry in the palette to opacity '\x00'
        img.info["transparency"] = b'\xff' * index_alpha + b'\x00'
    except UnboundLocalError:
        pass

    return img


def rgba_to_rgb(img):

    new_image_data = []

    for item in img.getdata():

        if item[3] < 50:
            new_image_data.append(ALPHA_COLOR)
        else:
            new_image_data.append(item[:3])

    new_image = Image.new("RGB", img.size)
    new_image.putdata(new_image_data)
    return new_image


def to_square(img):

    offsets = {
        "top": 0,
        "left": 0,
    }

    x, y = img.size
    if x == y:
        # already square
        return img, offsets

    size = max(x, y)

    if size == x:
        offsets["top"] = int((x - y)/2)
    else:
        offsets["left"] = int((x - y)/2)

    new_im = Image.new('RGB', (size, size), ALPHA_COLOR)
    new_im.paste(img, (offsets["left"], offsets["top"],))

    return new_im, offsets


def resize(f_bytes):
    """
    Take a APNG file in bytes in input, and returns a APNG object
    """

    new_apng = apng.APNG()

    master_palette = None

    for i, (png, control) in enumerate(apng.APNG.from_bytes(f_bytes).frames):

        pil_frame = Image.open(BytesIO(png.to_bytes()))

        if pil_frame.mode == "RGBA":
            pil_frame = rgba_to_rgb(pil_frame)
        elif pil_frame.mode == "P":
            pil_frame = rgba_to_rgb(pil_frame.convert("RGBA"))
        else:
            print("Error: mode non handled", pil_frame.mode)
            sys.exit(1)

        if i == 0:
            assert control.x_offset == 0
            assert control.y_offset == 0
            assert control.height != control.width

            pil_frame, offsets = to_square(pil_frame)
            pil_frame = pil_frame.quantize(colors=256, method=1)
            master_palette = pil_frame
            control.width = pil_frame.size[0]
            control.height = pil_frame.size[0]

        else:
            pil_frame = pil_frame.quantize(palette=master_palette)
            control.x_offset += offsets["left"]
            control.y_offset += offsets["top"]

        pil_frame = p_to_rgba(pil_frame)

        output = BytesIO()
        pil_frame.save(output, format="PNG")

        png_frame = apng.PNG.from_bytes(output.getvalue())

        fc = {
            "width":  control.width,
            "height":  control.height,
            "x_offset":  control.x_offset,
            "y_offset":  control.y_offset,
            "delay":  control.delay,
            "delay_den":  control.delay_den,
            "depose_op":  control.depose_op,
            "blend_op": control.blend_op,
        }

        new_apng.append(png_frame, **fc)

    return new_apng

