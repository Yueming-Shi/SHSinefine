# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import codecs
import io

from PIL import Image
from PIL import ImageEnhance


Image.preinit()
Image._initialized = 2

def image_resize_image(base64_source, size=(1024, 1024), encoding='base64', filetype=None, avoid_if_small=False, upper_limit=False):
    """ Function to resize an image. The image will be resized to the given
        size, while keeping the aspect ratios, and holes in the image will be
        filled with transparent background. The image will not be stretched if
        smaller than the expected size.
        Steps of the resizing:
        - Compute width and height if not specified.
        - if avoid_if_small: if both image sizes are smaller than the requested
          sizes, the original image is returned. This is used to avoid adding
          transparent content around images that we do not want to alter but
          just resize if too big. This is used for example when storing images
          in the 'image' field: we keep the original image, resized to a maximal
          size, without adding transparent content around it if smaller.
        - create a thumbnail of the source image through using the thumbnail
          function. Aspect ratios are preserved when using it. Note that if the
          source image is smaller than the expected size, it will not be
          extended, but filled to match the size.
        - create a transparent background that will hold the final image.
        - paste the thumbnail on the transparent background and center it.

        :param base64_source: base64-encoded version of the source
            image; if False, returns False
        :param size: 2-tuple(width, height). A None value for any of width or
            height mean an automatically computed value based respectively
            on height or width of the source image.
        :param encoding: the output encoding
        :param filetype: the output filetype, by default the source image's
        :type filetype: str, any PIL image format (supported for creation)
        :param avoid_if_small: do not resize if image height and width
            are smaller than the expected size.
    """
    if not base64_source:
        return False
    # Return unmodified content if no resize or we etect first 6 bits of '<'
    # (0x3C) for SVG documents - This will bypass XML files as well, but it's
    # harmless for these purposes
    if size == (None, None) or base64_source[:1] == b'P':
        return base64_source
    image_stream = io.BytesIO(codecs.decode(base64_source, encoding))
    image = Image.open(image_stream)
    # store filetype here, as Image.new below will lose image.format
    filetype = (filetype or image.format).upper()

    filetype = {
        'BMP': 'PNG',
    }.get(filetype, filetype)

    asked_width, asked_height = size
    if upper_limit:
        if asked_width:
            if asked_width >= image.size[0]:
                asked_width = image.size[0]
        if asked_height:
            if asked_height >= image.size[1]:
                asked_height = image.size[1]

        if image.size[0] >= image.size[1]:
            asked_height = None
        else:
            asked_width = None
        if asked_width is None and asked_height is None:
            return base64_source

    if asked_width is None:
        asked_width = int(image.size[0] * (float(asked_height) / image.size[1]))
    if asked_height is None:
        asked_height = int(image.size[1] * (float(asked_width) / image.size[0]))
    size = asked_width, asked_height
    # check image size: do not create a thumbnail if avoiding smaller images
    if avoid_if_small and image.size[0] <= size[0] and image.size[1] <= size[1]:
        return base64_source

    if image.size != size:
        image = image_resize_and_sharpen(image, size, upper_limit=upper_limit)
    if image.mode not in ["1", "L", "P", "RGB", "RGBA"] or (filetype == 'JPEG' and image.mode == 'RGBA'):
        image = image.convert("RGB")

    background_stream = io.BytesIO()
    image.save(background_stream, filetype)
    return codecs.encode(background_stream.getvalue(), encoding)

def image_resize_and_sharpen(image, size, preserve_aspect_ratio=False, factor=2.0, upper_limit=False):
    """
        Create a thumbnail by resizing while keeping ratio.
        A sharpen filter is applied for a better looking result.

        :param image: PIL.Image.Image()
        :param size: 2-tuple(width, height)
        :param preserve_aspect_ratio: boolean (default: False)
        :param factor: Sharpen factor (default: 2.0)
    """
    origin_mode = image.mode
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    image.thumbnail(size, Image.ANTIALIAS)
    if preserve_aspect_ratio:
        size = image.size
    sharpener = ImageEnhance.Sharpness(image)
    resized_image = sharpener.enhance(factor)
    # create a transparent image for background and paste the image on it
    if upper_limit:
        image = Image.new('RGBA', (size[0], size[1]-3), (255, 255, 255, 0)) # FIXME temporary fix for trimming the ghost border.
    else:
        image = Image.new('RGBA', size, (255, 255, 255, 0))
    image.paste(resized_image, ((size[0] - resized_image.size[0]) // 2, (size[1] - resized_image.size[1]) // 2))

    if image.mode != origin_mode:
        image = image.convert(origin_mode)
    return image