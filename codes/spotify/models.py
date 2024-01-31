from django.db import models

from django.contrib.auth import get_user_model

class Sog(models.Model):
    name = models.TextField()
    seconds = models.IntegerField(default=0)
    sog_group = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        null=True, blank=True, default=None
    )


class SogAub(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)



class Song(models.Model):
    artist_name = models.CharField(max_length=255)
    track_title = models.CharField(max_length=255)
    track_number = models.IntegerField()
    album_name = models.CharField(max_length=255)
    release_date = models.DateField()
    isrc = models.CharField(max_length=20, blank=True, null=True)
    album_art = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.artist_name} - {self.track_title}"

class DownloadedSong(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    download_date = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to="downloaded_songs/")

    def __str__(self):
        return f"{self.song.artist_name} - {self.song.track_title} - {self.download_date}"