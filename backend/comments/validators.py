from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from PIL import Image

allowed_file_extensions = FileExtensionValidator(
    allowed_extensions=['jpg', 'jpeg', 'gif', 'png', 'txt'],
    message='Allowed: JPG, GIF, PNG, TXT',
)


def validate_txt_size(file_obj):
    name = file_obj.name.lower()
    if not name.endswith('.txt'):
        return
    max_size = 100 * 1024
    if file_obj.size > max_size:
        raise ValidationError(
            f'TXT must be at most 100 KB. Current size: {file_obj.size / 1024:.1f} KB.'
        )


def resize_image_if_needed(file_obj):
    name = file_obj.name.lower()
    if name.endswith('.txt'):
        return file_obj
    if not name.endswith(('.jpg', '.jpeg', '.gif', '.png')):
        return file_obj

    image = Image.open(file_obj)
    max_size = (320, 240)

    if image.width <= max_size[0] and image.height <= max_size[1]:
        file_obj.seek(0)
        return file_obj

    image.thumbnail(max_size)
    buffer = BytesIO()
    fmt = image.format or 'PNG'
    if fmt.upper() == 'JPEG' and image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    image.save(buffer, format=fmt)
    buffer.seek(0)
    return ContentFile(buffer.read(), name=file_obj.name)
