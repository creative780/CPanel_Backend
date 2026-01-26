from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'
    
    def ready(self):
        """Import signals and validate email configuration on startup"""
        import hr.signals  # noqa
        
        # Validate email configuration
        try:
            from django.conf import settings
            from .services import validate_email_configuration
            
            # Only check if not in a migration or test
            import sys
            if 'migrate' in sys.argv or 'makemigrations' in sys.argv or 'test' in sys.argv:
                return
            
            validation = validate_email_configuration()
            
            if not validation['valid']:
                logger.warning("=" * 80)
                logger.warning("❌ EMAIL CONFIGURATION NOT VERIFIED - ISSUES DETECTED:")
                for error in validation['errors']:
                    logger.warning(f"  ❌ {error}")
                logger.warning("=" * 80)
                logger.warning("OTP emails will not be sent until email configuration is fixed.")
                logger.warning("See EMAIL_SETUP_GUIDE.md for configuration instructions.")
                logger.warning("=" * 80)
            else:
                if validation['warnings']:
                    logger.info("✅ Email configuration VERIFIED with warnings:")
                    for warning in validation['warnings']:
                        logger.info(f"  ⚠️  {warning}")
                else:
                    logger.info("✅ VERIFIED: Email configuration validated successfully")
        except Exception as e:
            # Don't fail startup if validation fails
            logger.warning(f"Could not validate email configuration on startup: {e}")