from typing import Annotated

from fastapi import Depends

from app.super_admin import models
from app.user import selectors as user_selectors

CurrentAdmin = Annotated[models.Admin, Depends(user_selectors.get_current_user)]
