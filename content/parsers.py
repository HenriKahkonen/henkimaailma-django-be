from rest_framework.parsers import BaseParser

class RawParser(BaseParser):
    """Accepts any media type, returns the raw body unparsed."""
    media_type = "*/*"

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()