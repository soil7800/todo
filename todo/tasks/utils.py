from transliterate import translit
from django.utils.text import slugify


def generate_slug_from_russian(text):
    text = translit(text, 'ru', reversed=True)
    slug = slugify(text)
    return slug

