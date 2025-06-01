// navigator.mediaDevices.getUserMedia({ video: true })
//   .then(stream => {
//     document.querySelector("#webcam").srcObject = stream;
//   })
//   .catch(err => {
//     console.log("Error accessing webcam:", err);
//   });





// let mediaRecorder;

// document.querySelector("#record-button").addEventListener("click", () => {
// if (mediaRecorder) {
//     // Stop recording
//     mediaRecorder.stop();
//     mediaRecorder = null;
//     document.querySelector("#record-button").innerHTML = "Start Recording";
// } else {
//     // Start recording
//     const stream = document.querySelector("#webcam").srcObject;
//     mediaRecorder = new MediaRecorder(stream);
//     mediaRecorder.start();
//     document.querySelector("#record-button").innerHTML = "Stop Recording";
// }
// });


// mediaRecorder.ondataavailable = event => {
//     const videoBlob = new Blob([event.data], { type: "video/webm" });
//     saveAs(videoBlob, "webcam-recording.webm");
//   };
















// //   navigator.mediaDevices.getUserMedia({ video: true, audio: false })
// //   .then(function(stream) {
// //     var video = document.querySelector('video');
// //     video.srcObject = stream;
// //     video.onloadedmetadata = function() {
// //       video.play();
// //       var duration = video.duration;
// //       console.log("Duration: " + duration + " seconds");
// //     };
// //     var mediaRecorder = new MediaRecorder(stream);
// //     var chunks = [];
// //     mediaRecorder.ondataavailable = function(e) {
// //       chunks.push(e.data);
// //     };
// //     mediaRecorder.onstop = function() {
// //       var blob = new Blob(chunks, { type: "video/webm" });
// //       var url = URL.createObjectURL(blob);
// //       var a = document.createElement("a");
// //       document.body.appendChild(a);
// //       a.style = "display: none";
// //       a.href = url;
// //       a.download = "video.webm";
// //       a.click();
// //       window.URL.revokeObjectURL(url);
// //     };
// //     document.querySelector("#start-recording").onclick = function() {
// //       mediaRecorder.start();
// //     };
// //     document.querySelector("#stop-recording").onclick = function() {
// //       mediaRecorder.stop();
// //     };
// //   })
// //   .catch(function(err) {
// //     console.log("An error occurred: " + err);
// //   });



const constraints = { "video": { width: { max: 320 } }, "audio" : true };

var theStream;
var theRecorder;
var recordedChunks = [];



function startFunction() {
  navigator.mediaDevices.getUserMedia(constraints)
      .then(gotMedia)
      .catch(e => { console.error('getUserMedia() failed: ' + e); });
}



function gotMedia(stream) {
  theStream = stream;
  var video = document.querySelector('video');
  video.srcObject = stream;
  try {
    recorder = new MediaRecorder(stream, {mimeType : "video/webm"});
  } catch (e) {
    console.error('Exception while creating MediaRecorder: ' + e);
    return;
  }
  
  theRecorder = recorder;
  recorder.ondataavailable = 
      (event) => { recordedChunks.push(event.data); };
  recorder.start(100);
}


function download() {
  theRecorder.stop();
  theStream.getTracks().forEach(track => { track.stop(); });

  var blob = new Blob(recordedChunks, {type: "video/webm"});
  var url =  URL.createObjectURL(blob);
  var a = document.createElement("a");
  document.body.appendChild(a);
  a.style = "display: none";
  a.href = url;
  a.download = 'test.webm';
  a.click();
  // setTimeout() here is needed for Firefox.
  setTimeout(function() { URL.revokeObjectURL(url); }, 100); 
}