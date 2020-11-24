//var video = videojs('test_video');
//var video = $("test_video")  // document.querySelector('video');
var video = document.getElementById("test_video");
//  player.duration = function() {
//  return 1000000; // the amount of seconds of video
//  }
//  player.src({
//    src: '/static/outfile.mp4',
//    type: 'video/mp4' //; codecs="avc1.42E01E, mp4a.40.2"'
//  });

var CHUNK_SIZE = 65536;
//var CHUNK_SIZE =
var FILE = '/static/outfile.mp4';

if (!window.MediaSource) {
  alert('The MediaSource API is not available on this platform');
}
var mediaSource = new MediaSource();
video.src = window.URL.createObjectURL(mediaSource);
// make an empty sourceBuffer
mediaSource.addEventListener('sourceopen', function() {
  var sourceBuffer = mediaSource.addSourceBuffer('video/mp4; codecs="avc1.640028"');
  console.log(sourceBuffer);
  console.log('MediaSource readyState: ' + this.readyState);
  get(FILE, function(uInt8Array) {
    var file = new Blob([uInt8Array], {
      type: 'video/mp4; codecs="avc1.640028"'
    });
//    var chunkSize = Math.ceil(file.size / NUM_CHUNKS);

    console.log('Chunk size: ' + CHUNK_SIZE + ', total size: ' + file.size);

    // Slice the video into NUM_CHUNKS and append each to the media element.
    var i = 0;
    var startByte = 0;
    (function readChunk_(i) { // eslint-disable-line no-shadow
      var reader = new FileReader();

      // Reads aren't guaranteed to finish in the same order they're started in,
      // so we need to read + append the next chunk after the previous reader
      // is done (onload is fired).
      reader.onload = function(e) {
        sourceBuffer.appendBuffer(new Uint8Array(e.target.result));
        console.log('Appending chunk from startByte: ' + startByte);
//        if (i === NUM_CHUNKS - 1) {
//          sourceBuffer.addEventListener('updateend', function() {
//            if (!sourceBuffer.updating && mediaSource.readyState === 'open') {
//              mediaSource.endOfStream();
//            }
//          });
//        } else {
        if (video.paused) {
          video.play(); // Start playing after 1st chunk is appended.
        }
        readChunk_(++i);
      };

//      var startByte = CHUNK_SIZE * i;
      var chunk = file.slice(startByte, startByte + CHUNK_SIZE);
      console.log('Chunk size = ' + chunk.size);
      reader.readAsArrayBuffer(chunk);
      startByte += chunk.size

    })(i); // Start the recursive call by self calling.
  });
}, false);

mediaSource.addEventListener('sourceended', function() {
  console.log('MediaSource readyState: ' + this.readyState);
}, false);

function get(url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.responseType = 'arraybuffer';
  xhr.send();


  xhr.onload = function() {
    if (xhr.status !== 200) {
      alert('Unexpected status code ' + xhr.status + ' for ' + url);
      return false;
    }
//    xhr.close();
//    xhr.open('GET', url, true);
//    xhr.responseType = 'arraybuffer';
//    xhr.send();

    callback(new Uint8Array(xhr.response));
  };
}

