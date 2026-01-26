"""
Django signals for automatic Matrix user synchronization
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_save)
def sync_user_to_matrix(sender, instance, created, **kwargs):
    """
    Automatically sync new users to Matrix when they are created
    """
    # Only process User model
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if sender != User:
        return
    
    # Only sync when a new user is created and is active
    if not created or not instance.is_active:
        return
    
    # Skip if already synced
    if instance.matrix_synced:
        return
    
    # Skip if Matrix service is not configured
    try:
        from accounts.services.matrix_service import matrix_service
        from django.conf import settings
        
        # Check if Matrix is configured
        if not getattr(settings, 'MATRIX_SHARED_SECRET', None):
            logger.debug(f"Matrix not configured, skipping sync for user {instance.username}")
            return
        
    except ImportError:
        logger.warning("Matrix service not available, skipping sync")
        return
    
    # Sync user to Matrix in background to avoid blocking user creation
    import threading
    
    def sync_user():
        try:
            from accounts.services.matrix_service import matrix_service
            import secrets
            
            # Generate password for Matrix user
            matrix_password = secrets.token_urlsafe(16)
            
            # Create display name
            display_name = instance.get_full_name() or instance.username
            
            # Determine if user should be admin in Matrix
            is_admin = instance.is_admin()
            
            # Create user in Matrix
            result = matrix_service.create_user(
                username=instance.username,
                password=matrix_password,
                display_name=display_name,
                admin=is_admin
            )
            
            if result:
                # Update user model with Matrix info
                instance.matrix_user_id = result.get('user_id')
                instance.matrix_synced = True
                
                # Create access token
                user_password = result.get('password')
                if user_password:
                    token = matrix_service.create_access_token(
                        instance.matrix_user_id,
                        device_id=f"crm-{instance.id}",
                        password=user_password
                    )
                    if token:
                        instance.matrix_access_token = token
                
                # Save user with Matrix info (refresh from DB to avoid stale instance)
                from django.contrib.auth import get_user_model
                User = get_user_model()
                User.objects.filter(pk=instance.pk).update(
                    matrix_user_id=instance.matrix_user_id,
                    matrix_synced=True,
                    matrix_access_token=instance.matrix_access_token
                )
                logger.info(f"✅ Automatically synced user {instance.username} to Matrix: {instance.matrix_user_id}")
            else:
                logger.warning(f"⚠️ Failed to sync user {instance.username} to Matrix")
        
        except Exception as e:
            logger.error(f"❌ Error syncing user {instance.username} to Matrix: {e}", exc_info=True)
    
    # Run sync in background thread to avoid blocking user creation
    thread = threading.Thread(target=sync_user, daemon=True)
    thread.start()

