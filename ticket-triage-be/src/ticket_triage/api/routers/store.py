"""Storefront router: categories, products, Amazon-style ABSA insights, and reviews."""

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from ...application.catalog_service import CatalogService
from ...application.review_service import ReviewService
from ...domain.entities import UserEntity
from ...domain.exceptions import ValidationDomainError
from ...domain.ports.storage import ImageStoragePort
from ..dependencies import (
    get_catalog_service,
    get_current_admin,
    get_current_user,
    get_image_storage,
    get_review_service,
)
from ..mappers import (
    to_category_out,
    to_insights_out,
    to_product_out,
    to_product_summary_out,
    to_review_out,
    to_review_triage_summary_out,
)
from ..schemas import (
    CategoryOut,
    ImageUploadResponse,
    ProductDetailResponse,
    ProductListResponse,
    ReviewCreateIn,
    ReviewCreateResponse,
)

router = APIRouter(prefix="/store", tags=["Storefront"])

# Disallow SVG uploads to prevent stored XSS on same-origin serving
_ALLOWED_IMAGE_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
_MAX_IMAGE_BYTES = 5 * 1024 * 1024


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> list[CategoryOut]:
    """Lấy danh sách danh mục sản phẩm kèm tổng số sản phẩm mỗi danh mục."""
    return [to_category_out(cat) for cat in catalog_service.list_categories()]


@router.get("/products", response_model=ProductListResponse)
def list_products(
    category: str | None = None,
    q: str | None = None,
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> ProductListResponse:
    """Lấy danh sách sản phẩm kèm chỉ số hài lòng AI và Top khía cạnh được đánh giá cao."""
    items, total = catalog_service.list_products(
        category_slug=category,
        search=q,
        limit=limit,
        offset=offset,
    )
    return ProductListResponse(
        items=[to_product_summary_out(entry) for entry in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/products/{slug}", response_model=ProductDetailResponse)
def get_product_detail(
    slug: str,
    aspect: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> ProductDetailResponse:
    """Lấy chi tiết sản phẩm, bảng xếp hạng Top 1-2-3 khía cạnh ABSA và danh sách bình luận."""
    detail = catalog_service.get_product_detail(
        slug=slug,
        aspect=aspect,
        review_limit=limit,
        review_offset=offset,
    )
    return ProductDetailResponse(
        product=to_product_out(detail.product),
        insights=to_insights_out(detail.insights),
        reviews=[to_review_out(r) for r in detail.reviews],
        total_filtered_reviews=detail.total_filtered_reviews,
    )


@router.post(
    "/products/{slug}/reviews",
    response_model=ReviewCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_product_review(
    slug: str,
    payload: ReviewCreateIn,
    current_user: UserEntity = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
) -> ReviewCreateResponse:
    """Gửi bình luận sản phẩm -> phân tích ABSA qua TriageGatewayPort -> tạo Admin Ticket."""
    res = review_service.submit_review(
        user=current_user,
        product_slug=slug,
        content=payload.content,
        title=payload.title,
    )
    return ReviewCreateResponse(
        review=to_review_out(res.review),
        triage=to_review_triage_summary_out(res.triage),
        insights=to_insights_out(res.insights),
    )


@router.post(
    "/uploads/image",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_product_image(
    file: UploadFile = File(...),
    _admin: UserEntity = Depends(get_current_admin),
    image_storage: ImageStoragePort = Depends(get_image_storage),
) -> ImageUploadResponse:
    """Admin tải ảnh sản phẩm lên ImageStoragePort (Cloudinary hoặc Local fallback)."""
    if file.content_type not in _ALLOWED_IMAGE_TYPES:
        raise ValidationDomainError("Chỉ hỗ trợ định dạng ảnh JPEG, PNG hoặc WebP.")
    content = file.file.read(_MAX_IMAGE_BYTES + 1)
    if len(content) > _MAX_IMAGE_BYTES:
        raise ValidationDomainError("Kích thước ảnh vượt quá giới hạn tối đa 5 MB.")
    if not content:
        raise ValidationDomainError("Tệp ảnh không được để trống.")

    url = image_storage.upload_image(
        content=content,
        filename=file.filename or "product.png",
        folder="products",
    )
    return ImageUploadResponse(image_url=url)
