$(document).ready(function() {

  var user_tracks = [];
  var playlist_tracks;
  var userid;
  var params = getHashParams();
  var access_token = params.access_token,
      refresh_token = params.refresh_token,
      playlist_option = params.pl,
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
        alert("You need an access token to view this page.");
    }

    $('#go-to-playlist').click(function() {
      console.log("go to");
      window.location.href = '/playlist#access_token=' + access_token + "&refresh_token=" + refresh_token + "&pl=" + playlist_option;
    })
    // onclick handler for build-playlist button
    $('build-playlist').click(function() {
      data = {'tracks':user_tracks}
      $.ajax({
          type : "POST",
          url : "/api/build",
          data: JSON.stringify(data, null, '\t'),
          contentType: 'application/json;charset=UTF-8',
          success: function(result) {
              $('#loading-playlist').removeClass('hidden');
              buildPlaylist(result);
          }
      });
    });

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

});
