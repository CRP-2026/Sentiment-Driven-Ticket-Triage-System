from fastapi import APIRouter, Request
from ..schemas import AspectMetaItem

router = APIRouter(prefix="/meta", tags=["Metadata"])

@router.get("/aspects", response_model=list[AspectMetaItem])
def get_aspects_metadata(request: Request) -> list[AspectMetaItem]:
    taxonomy = getattr(request.app.state, "taxonomy", None)
    if taxonomy is None:
        return []

    return [
        AspectMetaItem(
            id=a.id,
            name_vi=a.name_vi,
            description=a.description,
            department=a.department,
            weight=a.weight,
        )
        for a in taxonomy.get_all()
    ]
