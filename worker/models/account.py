from datetime import date
from datetime import datetime
import spotipy
from boto.dynamodb2.table import Table
from worker.spotify.api import new_access_token
from spotify_playlist import PlaylistEntry


class Account(object):

    def __init__(self, username):
        self._username = username
        self._model = self._database_model()
        self._spotify = self._spotify_client()

    def __repr__(self):
        return "<Account: {0} - {1}>".format(self._username, self._model['spotify_playlist_id'])

    def _database_model(self):
        accounts = Table('accounts')
        return accounts.get_item(
            spotify_username=self._username)

    def _spotify_client(self):
        self._refresh_access_token()
        return spotipy.Spotify(auth=self._model['access_token'])

    def _refresh_access_token(self):
        self._model['access_token'] = new_access_token(self._model['refresh_token'])
        self._model.save()

    def playlist_entry(self, added_date=date.isoformat(date.today())):
        def was_added_today(item):
            added_at = datetime.strptime(item['added_at'], '%Y-%m-%dT%H:%M:%SZ')
            return added_date == date.isoformat(added_at.date())

        offset = 0
        entry = None
        while True:
            result = self._spotify.user_playlist_tracks(
                self._username,
                self._model['spotify_playlist_id'],
                offset=offset)
            try:
                item = filter(was_added_today, result['items'])[0]
                entry = PlaylistEntry(**item)
                break
            except IndexError:
                if result['next']:
                    offset += 50
                else:
                    break
        return entry

    def feed_item(self, added_date=date.isoformat(date.today())):
        playlist_entry = self.playlist_entry(added_date=added_date)
        feed_item = None
        if playlist_entry:
            feed_item = {'spotify_username': self._username}
            feed_item.update(playlist_entry.feed_item())
        return feed_item

    def update_last_processed(self, processed_date):
        self._model['last_processed'] = processed_date
        self._model.save()
