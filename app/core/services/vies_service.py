"""
VAT validation service for Translate-Descriptions application.

This module implements business logic for VAT number validation
using the VIES SOAP service.
"""

from typing import Optional
from zeep import Client, exceptions
from app.core.domain.interfaces import IViesService
from app.core.domain.models import VATValidationResult
from app.core.domain.exceptions import VIESError
from app.core.domain.interfaces import ILogger


class ViesService(IViesService):
    """Service for VAT number validation.
    
    Implements IViesService interface using VIES SOAP service.
    Provides retry logic for transient failures.
    """
    
    def __init__(
        self,
        wsdl_url: str,
        logger: ILogger,
        max_retries: int = 3
    ):
        """Initialize VIES service.
        
        Args:
            wsdl_url: VIES WSDL URL
            logger: Logger instance
            max_retries: Maximum retry attempts (default: 3)
        """
        self._wsdl_url = wsdl_url
        self._logger = logger
        self._max_retries = max_retries
    
    def validate_vat(self, country_code: str, vat_number: str) -> VATValidationResult:
        """Validate VAT number via VIES service.
        
        Args:
            country_code: Two-letter country code (e.g., "PL", "DE")
            vat_number: VAT number to validate
            
        Returns:
            VATValidationResult with validation status and company info
            
        Raises:
            VIESError: If validation fails after retries
        """
        from app.shared.decorators.retry_decorator import retry
        
        @retry(
            max_attempts=self._max_retries,
            delay=1.0,
            backoff_factor=2.0,
            exceptions=(exceptions.Fault, Exception)
        )
        def _validate():
            client = Client(self._wsdl_url)
            
            if self._logger:
                self._logger.debug(
                    f"Validating VAT: {country_code}{vat_number}"
                )
            
            try:
                result = client.service.checkVat(
                    countryCode=country_code,
                    vatNumber=vat_number
                )
                
                return VATValidationResult(
                    valid=result.valid,
                    name=result.name if result.valid else None,
                    address=result.address if result.valid else None,
                    country_code=country_code,
                    vat_number=vat_number
                )
                
            except exceptions.Fault as fault:
                error_msg = f"VIES fault: {fault}"
                if self._logger:
                    self._logger.error(error_msg)
                raise VIESError(error_msg) from fault
            
            except Exception as e:
                error_msg = f"VIES validation error: {e}"
                if self._logger:
                    self._logger.error(error_msg)
                raise VIESError(error_msg) from e
        
        return _validate()
