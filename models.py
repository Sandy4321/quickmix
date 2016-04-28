class Track(object):
	def __init__(self,trackID,artistID=None,title=None):
		self.trackID = trackID
		self.artistID = artistID
		self.title = title

class Playlist(object):
	def __init__(self,tracks=None):
		self.tracks = tracks

	def add_track(self,track):
		self.tracks.append(track)

	def __iter__(self):
		for track in self.tracks:
			yield track


