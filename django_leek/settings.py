from django.conf import settings


SECRET_KEY="just to make tests run"

cfg = getattr(settings, "LEEK", {})
        
MAX_RETRIES = cfg.get('max_retries', 3)
HOST = cfg.get('host', "localhost")
PORT = int(cfg.get('port', "8002"))
