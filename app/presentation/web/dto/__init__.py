"""
Data Transfer Objects for API requests and responses.
"""
from app.presentation.web.dto.translation_dto import (
    TranslationRequest,
    TranslationResponse,
    GenerationRequest,
    GenerationResponse,
    RephraseRequest,
    RephraseResponse,
)
from app.presentation.web.dto.product_dto import (
    ProductDescriptionRequest,
    ProductInfoWithSizecodeRequest,
    ProductFullInfoWithSizecodeRequest,
    ProductFullInfoWithEanRequest,
    ProductImagesRequest,
    ProductsInfoRequest,
    SetProductDescriptionRequest,
    PaginationResponse,
)
from app.presentation.web.dto.auth_dto import (
    AuthenticationRequest,
    AuthenticationResponse,
    TokenValidationResponse,
    TokenRefreshResponse,
    LogoutResponse,
    BearerTokenResponse,
)

__all__ = [
    "TranslationRequest",
    "TranslationResponse",
    "GenerationRequest",
    "GenerationResponse",
    "RephraseRequest",
    "RephraseResponse",
    "ProductDescriptionRequest",
    "ProductInfoWithSizecodeRequest",
    "ProductFullInfoWithSizecodeRequest",
    "ProductFullInfoWithEanRequest",
    "ProductImagesRequest",
    "ProductsInfoRequest",
    "SetProductDescriptionRequest",
    "PaginationResponse",
    "AuthenticationRequest",
    "AuthenticationResponse",
    "TokenValidationResponse",
    "TokenRefreshResponse",
    "LogoutResponse",
    "BearerTokenResponse",
]
