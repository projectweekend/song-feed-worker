from datetime import datetime
from datetime import date
from spotify_item import SpotifyItem
from spotify_track import Track


class PlaylistEntry(SpotifyItem):

    def __init__(self, **entries):
        super(PlaylistEntry, self).__init__(**entries)
        self.track = Track(**self.track)
        self.added_at = datetime.strptime(self.added_at, '%Y-%m-%dT%H:%M:%SZ')
        self.added_date = self.added_at.date()

    def __repr__(self):
        return '<PlaylistEntry: {0}>'.format(self.track.name)

    def feed_item(self):
        return {
            'date_posted': date.isoformat(self.added_date),
            'track': self.track.export_for_feed(),
            'album': self.track.album.export_for_feed(),
            'artists': [a.export_for_feed() for a in self.track.artists]
        }
