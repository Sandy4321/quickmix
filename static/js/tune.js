$(document).ready(function() {

  var user_tracks = [];
  var playlist_tracks;
  var userid;
  var access_token = getURLParam("access_token");
  var refresh_token = getURLParam("refresh_token");
  var playlist_type = getURLParam("pl");
  var error = getURLParam("error");

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
            console.log('spotify results')
            for (i in response.items){
              user_tracks.push({'id':response.items[i].id,'artist':response.items[i].artists[0].id})
            }
            data = {'tracks':user_tracks,'category':'chill'}
            $.ajax({
                type : "POST",
                url : "/api/validate",
                data: JSON.stringify(data, null, '\t'),
                contentType: 'application/json;charset=UTF-8',
                success: function(result) {
                  console.log(result)
                  $('.song-info-loading').hide();
                  $('.influencers').removeClass("hidden");
                  $('#loggedin').show();
                }
            });
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

});

/*
Parses params from URLS - uses location.search (requires ?var=a&var=b syntax - No hashes)
http://stackoverflow.com/a/11582513
*/
function getURLParam(name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}
