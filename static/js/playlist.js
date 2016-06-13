///////////// Knockout.js definitions //////////////

function Song(trackid, title, artist, coverart, previewURL, uri) {
    var self = this;
    self.trackid = trackid
    self.title = title;
    self.artist = artist;
    self.coverart = coverart;
    self.preview = new Audio(previewURL);
    self.uri = uri;
}

// Overall viewmodel for this screen, along with initial state
function PlaylistViewModel() {
    var self = this;

    // Editable data
    self.songs = ko.observableArray();

    self.moodSpectrum = ko.observable(true)
    self.moodOption = ko.observable("option2")

    
    // Operations
    self.addSong = function(trackid,title,artist,coverart,previewURL,uri) {
      self.songs.push(new Song(trackid,title,artist,coverart,previewURL,uri));     
    }   

    self.pauseAll = function(){
      for (i in self.songs()){
        self.songs()[i].preview.pause();
      }
    }

    self.playSong = function(song) {
      if (song.preview.paused) {
        self.pauseAll();
        song.preview.play();
      }
      else{
        self.pauseAll();
      }
    }

    self.checkboxClicked = function(song) {
      console.log(song.includeInfluencer())
      if (song.includeInfluencer()) {
        song.includeInfluencer(false);
      }
      else{
        song.includeInfluencer(true);
      }
      console.log(song.includeInfluencer())
    }  
}

PVM = new PlaylistViewModel();

ko.applyBindings(PVM);

////////////////////////////////////////////////////

function removeOverlay(URL) {
  document.getElementById("spotifyOverlay").style.height = "0%";
}

function getURLParam(name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}

$(document).ready(function() {
  var user_tracks = getURLParam("trackids");
  var pl = getURLParam("pl");
  var playlist_option = getURLParam("playlist_option");
  data = {'tracks':user_tracks.split(','),'pl':pl,'playlist_option':playlist_option}
  console.log(data)
  $.ajax({
      type : "POST",
      url : "/api/build",
      data: JSON.stringify(data, null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
          // $('#loading-playlist').removeClass('hidden');
          buildPlaylist(result.data.playlist);
          console.log(result)
          $('.song-info-loading').hide();
          $('.influencers').removeClass("hidden");
          removeOverlay();
      }
    });


  var access_token = getURLParam("access_token");
  var refresh_token = getURLParam("refresh_token");
  var playlist_type = getURLParam("pl");
  var error = getURLParam("error");
  var userid;

  if (error) {
    alert('There was an error during the authentication');
  } else {
    if (access_token) {

      $.ajax({
          url: 'https://api.spotify.com/v1/me/',
          headers: {
            'Authorization': 'Bearer ' + access_token
          },
          success: function(response) {
            userid = response.id
          }
      });

    } else {
        // render initial screen
        $('#login').show();
        $('#loggedin').hide();
    }

    /////////// PLAYLIST
    // Export playlist
    $('.export-button').click(function() {
      data = {
        "name": "Song you might like for what you are doing.",
        "public": false
      }
      $.ajax({
        type : "POST",
        url : "https://api.spotify.com/v1/users/"+userid+"/playlists",
        data: JSON.stringify(data, null, '\t'),
        headers: {
          'Authorization': 'Bearer ' + access_token
        },
        contentType: 'application/json;charset=UTF-8',
        success: function(result) {
          playlist_id = result.id;
          var tracklist = [];
          for (i in PVM.songs()){
            tracklist.push(PVM.songs()[i].uri)
          }
          // Populate playlist with tracks
          $.ajax({
            type : "POST",
            url : "https://api.spotify.com/v1/users/"+userid+"/playlists/"+playlist_id+"/tracks?uri",
            data: JSON.stringify({'uris':tracklist}, null, '\t'),
            headers: {
              'Authorization': 'Bearer ' + access_token
            },
            contentType: 'application/json;charset=UTF-8',
            success: function(result) {
              console.log('exported!');
              $('#exporting-complete').removeClass('hidden');
            }
          });
        }
      });
    });
  }

  function buildPlaylist(tracks) {
    console.log('building')
    tracklist = [];
    for (i in tracks) {
      tracklist.push(tracks[i].id)
    }

    $.ajax({
        url: 'https://api.spotify.com/v1/tracks',
        data: {'ids':tracklist.join()},
        headers: {
          'Authorization': 'Bearer ' + access_token
        },
        success: function(response) {
          console.log(response)
          tracks = response.tracks
          for (i in tracks) {
            // console.log(tracks[i].id,tracks[i].title,tracks[i].artist,tracks[i].coverart,tracks[i].previewURL);
            console.log(tracks[i])
            PVM.addSong(tracks[i].id,tracks[i].name,tracks[i].artists[0].name,tracks[i].album.images[1].url,tracks[i].preview_url,tracks[i].uri);
          }
        }
    });
  }

});
