# VISITOR_ACCESS_LEVEL: int = 1
# MODERATOR_ACCESS_LEVEL: int = 2
# ADMIN_ACCESS_LEVEL: int = 3
MEDIA_PER_PAGE: int = 10
FLASH_DURATION: int = 5000

ACCESS_LEVEL_MAP = {
    'visitor': 1,
    'moderator': 2,
    'administrator': 3
}

ALLOWED_MIME_TYPES = [
    'image/avif',
    'image/jpeg',
    'image/png',
    'image/webp'
]