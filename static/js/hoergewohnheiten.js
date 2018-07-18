function get(url, callback) {
    $.ajax({
        url: url,
        dataType: 'text',
        success: function (data) {
			callback(JSON.parse(data))
        },
        error: function () {
            console.log('Failed!')
        }
    });
}

function applyArtistStats(topArtists) {
    var table = $('<table>').attr('class', 'table table-striped');
    var tableBody = $('<tbody>')
        .attr('class', 'table-body')
        .appendTo(table);
    table.appendTo($('#top-artists'));

    for (var i = 0; i <= Object.keys(topArtists).length; i++) {
        var countEntry = topArtists[i];
        var row = $('<tr>');
            $('<td>')
            .html(i+1)
            .appendTo(row);
        $('<img>')
            .attr('src', countEntry.artist.image_url)
            .attr('class', 'album-cover')
            .appendTo($('<td>').appendTo(row));
        $('<a>')
            .attr('href', countEntry.artist.spotify_url)
            .html(countEntry.artist.name)
            .appendTo($('<td>').appendTo(row));
        $('<td>')
            .html(countEntry.count)
            .appendTo(row);
        row.appendTo(tableBody);
    } 
}

function applyAlbumStats(topAlbum) {
    var table = $('<table>').attr('class', 'table table-striped');
    var tableBody = $('<tbody>')
        .attr('class', 'table-body')
        .appendTo(table);
    table.appendTo($('#top-albums'));


    for (var i = 0; i < Object.keys(topAlbum).length; i++) {
        var countEntry = topAlbum[i];
        var row = $('<tr>');
        $('<td>')
            .html(i+1)
            .appendTo(row);
        $('<img>')
            .attr('src', countEntry.album.image_url)
            .attr('class', 'album-cover')
            .appendTo($('<td>').appendTo(row));

        if (countEntry.album.artists.length > 0) {
            artist = countEntry.album.artists[0]
            var artistName = artist.name
        } else {
            var artistName = 'n/a'
        }
        $('<a>')
            .attr('href',countEntry.album.spotify_url)
            .html(artistName + ' - ' + countEntry.album.name)
            .appendTo($('<td>').appendTo(row));
        $('<td>')
            .html(countEntry.count)
            .appendTo(row);
        row.appendTo(tableBody);
    }
}

function applyTrackStats(topTracks) {
    var table = $('<table>').attr('class', 'table table-striped');
    var tableBody = $('<tbody>')
        .attr('class', 'table-body')
        .appendTo(table);
    table.appendTo($('#top-tracks'));


    for (var i = 0; i < Object.keys(topTracks).length; i++) {
        var countEntry = topTracks[i];
        var row = $('<tr>');
        $('<td>')
            .html(i+1)
            .appendTo(row);
        $('<img>')
            .attr('src', countEntry.track.album.image_url)
            .attr('class', 'album-cover')
            .appendTo($('<td>').appendTo(row));

        if (countEntry.track.artists.length > 0) {
            artist = countEntry.track.artists[0]
            var artistName = artist.name
        } else {
            var artistName = 'n/a'
        }
        $('<a>')
            .attr('href',countEntry.track.spotify_url)
            .html(artistName + ' - ' + countEntry.track.name)
            .appendTo($('<td>').appendTo(row));
        $('<td>')
            .html(countEntry.count)
            .appendTo(row);
        row.appendTo(tableBody);
    }
}

function applyAlbum(stats) {
    applyAlbumStats(stats.data)
}

function applyArtist(stats) {
    applyArtistStats(stats.data)
}

function applyTrack(stats) {
    applyTrackStats(stats.data)
}


function applyPlays(plays) {
    latestPlays = plays['latest_plays']
    for (var i = 0; i < Object.keys(latestPlays).length; i++) {
        var trackName = latestPlays[i].track.name
        if (latestPlays[i].track.artists.length > 0) {
            artist = latestPlays[i].track.artists[0]
            var artistName = artist.name
        } else {
            var artistName = 'n/a'
        }
        $('<li>')
            .attr('class', 'list-group-item')
            .html(artistName + ' - ' + trackName)
            .appendTo($('#latest-plays'))
    }
}

function getUrlAppendix(userName, fromDate, toDate) {
    urlAppendix = userName
    if (fromDate != null) {
        urlAppendix = urlAppendix + '/from/' + fromDate
        if (toDate != null) {  // toDate only if fromDate is given
            urlAppendix = urlAppendix + '/to/' + toDate
        }
    }
    return urlAppendix
}

function applyData() {
    var url = new URL(window.location.href);
    var userName = url.searchParams.get('user')
    var fromDate = url.searchParams.get('from')
    var toDate = url.searchParams.get('to')
    urlAppendix = getUrlAppendix(userName, fromDate, toDate)

    get('counts/per/track/user/' + urlAppendix, applyTrack)
    get('counts/per/artist/user/' + urlAppendix, applyArtist)
    get('counts/per/album/user/' + urlAppendix, applyAlbum)
}

$(document).ready(function () {
    applyData()
});
