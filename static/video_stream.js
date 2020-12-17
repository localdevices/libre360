// this javascript code streams a video (passed by netcat from child) via a file to a video tag.
// it is very inefficient to use, so we left it behind, but maybe it'll become useful later....
var video = document.querySelector('video');

var assetURL = '/static/outfile.mp4';
// Need to be specific for Blink regarding codecs
var mimeCodec = 'video/mp4; codecs="avc1.640028"';
var segmentLength = 65536;
var bytesFetched = 0;
var mediaSource = null;

if ('MediaSource' in window && MediaSource.isTypeSupported(mimeCodec)) {
  mediaSource = new MediaSource;
  video.src = URL.createObjectURL(mediaSource);
  mediaSource.addEventListener('sourceopen', sourceOpen);
} else {
  console.error('Unsupported MIME type or codec: ', mimeCodec);
}
var sourceBuffer = null;

function sourceOpen (_) {
  sourceBuffer = mediaSource.addSourceBuffer(mimeCodec);
  getFileLength(assetURL, function (fileLength) {
    console.log((fileLength / 1024 / 1024).toFixed(2), 'MB');

    console.log("Total length = " + fileLength + " Segment length =" + segmentLength);
    fetchRange(assetURL, 0, segmentLength, fileLength, appendSegment);
    video.addEventListener('timeupdate', addChunk);
      video.play();
  });
};

function getFileLength (url, callback) {
  var xhr = new XMLHttpRequest;
  xhr.open('head', url);
  xhr.onload = function () {
      callback(xhr.getResponseHeader('content-length'));
    };
  xhr.send();
};

function fetchRange (url, start, end, fileLength, cb) {
  var xhr = new XMLHttpRequest;
  xhr.open('get', url);
  xhr.responseType = 'arraybuffer';
  xhr.setRequestHeader('Range', 'bytes=' + start + '-' + end);
  xhr.onload = function () {
    // never retrieve more than the length of the file
    start = Math.min(start, fileLength)
    console.log("Length video = " + video.duration + ", current position" + video.currentTime)
    end = Math.min(end, fileLength)
    console.log('fetched bytes: ', start, end);
    bytesFetched += end - start + 1;
    cb(xhr.response);
  };
  xhr.send();
};

function appendSegment (chunk) {
  sourceBuffer.appendBuffer(chunk);
};


function addChunk (_) {
  // retrieve the current file length and stuff into a var
  getFileLength(assetURL, function(fileLength){
  // never retrieve more than the file length
    if (bytesFetched < fileLength){
        console.log("File length = " + fileLength + "bytesFetched = " + bytesFetched);
        fetchRange(assetURL, bytesFetched, bytesFetched + segmentLength, fileLength, appendSegment);
      }
  });
};
