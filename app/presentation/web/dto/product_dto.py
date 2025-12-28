"""
Data Transfer Objects for product-related requests and responses.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class ProductDescriptionRequest:
    """DTO for product description requests."""
    product_id: str
    shop_id: str
    lang: Optional[str] = None
    fields: Optional[List[str]] = None

    def validate(self) -> Optional[str]:
        """
        Validate product description request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.product_id:
            return "product_id is required"

        if not self.shop_id:
            return "shop_id is required"

        return None


@dataclass
class ProductInfoWithSizecodeRequest:
    """DTO for product info with sizecode requests."""
    barcodes: List[str]

    def validate(self) -> Optional[str]:
        """
        Validate product info with sizecode request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.barcodes or not isinstance(self.barcodes, list):
            return "barcodes list is required"

        if len(self.barcodes) == 0:
            return "barcodes list cannot be empty"

        return None


@dataclass
class ProductFullInfoWithSizecodeRequest:
    """DTO for full product info with sizecode requests."""
    product_id: str
    size_code: str

    def validate(self) -> Optional[str]:
        """
        Validate full product info with sizecode request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.product_id:
            return "product_id is required"

        if not self.size_code:
            return "size_code is required"

        return None


@dataclass
class ProductFullInfoWithEanRequest:
    """DTO for full product info with EAN requests."""
    ean: str

    def validate(self) -> Optional[str]:
        """
        Validate full product info with EAN request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.ean:
            return "ean is required"

        return None


@dataclass
class ProductImagesRequest:
    """DTO for product images requests."""
    product_ids: List[str]

    def validate(self) -> Optional[str]:
        """
        Validate product images request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.product_ids or not isinstance(self.product_ids, list):
            return "product_ids list is required"

        if len(self.product_ids) == 0:
            return "product_ids list cannot be empty"

        return None


@dataclass
class ProductsInfoRequest:
    """DTO for products info requests."""
    product_ids: List[str]
    page: int = 0
    limit: int = 10

    def validate(self) -> Optional[str]:
        """
        Validate products info request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.product_ids or not isinstance(self.product_ids, list):
            return "product_ids list is required"

        if len(self.product_ids) == 0:
            return "product_ids list cannot be empty"

        if self.page < 0:
            return "page must be >= 0"

        if self.limit < 1 or self.limit > 100:
            return "limit must be between 1 and 100"

        return None


@dataclass
class SetProductDescriptionRequest:
    """DTO for setting product descriptions requests."""
    product_descriptions: List[Dict[str, Any]]

    def validate(self) -> Optional[str]:
        """
        Validate set product description request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.product_descriptions or not isinstance(self.product_descriptions, list):
            return "product_descriptions list is required"

        if len(self.product_descriptions) == 0:
            return "product_descriptions list cannot be empty"

        for desc in self.product_descriptions:
            if not isinstance(desc, dict):
                return "each product description must be a dictionary"

            if "productId" not in desc:
                return "each product description must have a productId"

            if "productDescriptionsLangData" not in desc:
                return "each product description must have productDescriptionsLangData"

        return None


@dataclass
class PaginationResponse:
    """DTO for pagination responses."""
    current_page: int
    results_limit: int
    total_pages: int
    total_results: int
    has_next_page: bool
    has_prev_page: bool
    next_page: Optional[str]
    prev_page: Optional[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "current_page": self.current_page,
            "results_limit": self.results_limit,
            "total_pages": self.total_pages,
            "total_results": self.total_results,
            "has_next_page": self.has_next_page,
            "has_prev_page": self.has_prev_page,
            "next_page": self.next_page,
            "prev_page": self.prev_page
        }
