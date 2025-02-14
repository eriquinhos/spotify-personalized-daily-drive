from apscheduler.schedulers.background import BackgroundScheduler
from playlist_manager import PlaylistManager

def setup_scheduler(sp):
    """
    Set up the background scheduler for daily playlist updates.
    
    Args:
        sp (spotipy.Spotify): Authenticated Spotify client.
    
    Returns:
        BackgroundScheduler: Configured scheduler object.
    """
    scheduler = BackgroundScheduler()
    playlist_manager = PlaylistManager(sp)
    
    @scheduler.scheduled_job('cron', hour=0)  # Run every day at midnight
    def update_daily_drive_job():
        playlist_manager.update_daily_drive()
    
    scheduler.start()
    return scheduler

