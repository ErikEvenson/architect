import re
import unicodedata


def generate_slug(name: str) -> str:
    """Generate a URL-safe slug from a name."""
    # Normalize unicode characters
    slug = unicodedata.normalize("NFKD", name)
    # Remove non-ASCII characters
    slug = slug.encode("ascii", "ignore").decode("ascii")
    # Convert to lowercase
    slug = slug.lower()
    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    return slug
