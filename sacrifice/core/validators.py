from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class FileSizeValidator:
    """
    Max file size validator for Django FileField and ImageField.
    :param max_size_mb: Maximum file size in MB.
    """
    def __init__(self, max_size_mb: int = 2):
        self.message = f"Dosya boyutu {max_size_mb}MB'dan büyük olamaz."
        self.code = 'max_size'
        self.max_size = int(max_size_mb) * 1024 * 1024  # MB to Bytes

    def __call__(self, value):
        filesize = value.size
        if filesize > self.max_size:
            raise ValidationError(
                self.message, code=self.code, params={'max_size': self.max_size, 'filesize': filesize})

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.max_size == other.max_size
