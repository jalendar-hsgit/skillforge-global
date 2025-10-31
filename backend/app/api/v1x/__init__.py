from .courses_db import router as courses_db
from .progress_db import router as progress_db
from .quizzes_db import router as quizzes_db
# from .youtube_sync import router as youtube_sync  # Requires dateutil package
from .coins_db import router as coins_db

__all__ = ["courses_db", "progress_db", "quizzes_db", "coins_db"]
