import os
from pathlib import Path
from django.db.models.signals import post_save, post_delete 
from django.dispatch import receiver
from django.conf import settings
from .models import Video
from .tasks import convert_to_hls, generate_thumbnail



@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes files from filesystem when the Video object is deleted.
    """
    if instance.video_file and instance.video_file.name:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)

    hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(instance.id)
    if hls_dir.exists() and hls_dir.is_dir():
        for root, dirs, files in os.walk(hls_dir, topdown=False):
            for name in files:
                os.remove(Path(root) / name)
            for name in dirs:
                os.rmdir(Path(root) / name)
        hls_dir.rmdir()


        
    
            