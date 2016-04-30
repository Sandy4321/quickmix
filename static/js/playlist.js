$(document).ready(function() {

  var user_tracks = [];
  var playlist_tracks;
  var userid;
  var params = getHashParams();
  var access_token = params.access_token,
      refresh_token = params.refresh_token,
      error = params.error;

  if (error) {
    alert('There was an error during the authentication');
  } else {
    if (access_token) {
      $.ajax({
          url: 'https://api.spotify.com/v1/me/top/tracks?limit=100',
          headers: {
            'Authorization': 'Bearer ' + access_token
          },
          success: function(response) {
            for (i in response.items){
              user_tracks.push({'id':response.items[i].id,'artist':response.items[i].artists[0].id})
            }
            $('#login').hide();
            $('#loggedin').show();
          }
      });

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
    $('export-playlist').click(function() {
    data = {
      "name": "MyRunningSongs are in this playlist.",
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
        for (i in playlist_tracks.tracks){
          tracklist.push(playlist_tracks.tracks[i].uri)
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
      //TODO ON BACKEND REFRESH TOKEN
      // document.getElementById('obtain-new-token').addEventListener('click', function() {
      //   $.ajax({
      //     url: '/refresh_token',
      //     data: {
      //       'refresh_token': refresh_token
      //     }
      //   }).done(function(data) {
      //     access_token = data.access_token;
      //     oauthPlaceholder.innerHTML = oauthTemplate({
      //       access_token: access_token,
      //       refresh_token: refresh_token
      //     });
      //   });
      // }, false);
  }

  /**
   * Obtains parameters from the hash of the URL
   * @return Object
   */
  function getHashParams() {
    var hashParams = {};
    var e, r = /([^&;=]+)=?([^&;]*)/g,
        q = window.location.hash.substring(1);
    while ( e = r.exec(q)) {
       hashParams[e[1]] = decodeURIComponent(e[2]);
    }
    return hashParams;
  }

  function buildPlaylist(tracks) {
    var tracklist = [];
    for (i in tracks.data.playlist) {
      tracklist.push(tracks.data.playlist[i].id)
    }

    $.ajax({
        url: 'https://api.spotify.com/v1/tracks',
        data: {'ids':tracklist.join()},
        headers: {
          'Authorization': 'Bearer ' + access_token
        },
        success: function(response) {
          playlist_tracks = response;
          $playlisttracks = $('#playlist-tracks')
          for (i in response.tracks){
            $playlisttracks.append('<div class="track row">'+
              '<div class="song col-xs-4">'+response.tracks[i].name+'</div>'+
              '<div class="artist col-xs-4">'+response.tracks[i].artists[0].name+'</div>'+
              '<div class="album col-xs-4">'+response.tracks[i].album.name+'</div>'+
              '</div>')
          }

          $playlisttracks.removeClass('hidden')
          $('#loading-playlist').addClass('hidden');
          $('#export-playlist').removeClass('hidden');
        }
    });
  }

});
