# utils.py
from django.utils.text import slugify

def generate_unique_slug(model, title):
    base_slug = slugify(title)
    slug = base_slug
    n = 1
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{n}"
        n += 1
    return slug