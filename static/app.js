function send(){
    let q=document.getElementById("question").value;
    fetch("/ask",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({question:q})
    })
    .then(r=>r.json())
    .then(d=>location.reload());
}
