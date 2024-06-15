from typing import Annotated

from fastapi import Depends

from app.super_admin import models, selectors

CurrentAdmin = Annotated[models.Admin, Depends(selectors.get_current_admin)]
