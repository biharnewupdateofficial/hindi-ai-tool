function send(){
  let q = document.getElementById("question").value;
  if(!q) return;

  fetch("/ask",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({question:q})
  }).then(()=>location.reload());
}

function toggleTheme(){
  document.body.classList.toggle("dark");
}

// 🎤 VOICE INPUT
function startMic(){
  let rec = new webkitSpeechRecognition();
  rec.lang = "hi-IN";
  rec.onresult = e=>{
    document.getElementById("question").value = e.results[0][0].transcript;
  };
  rec.start();
}
