
function switchVideo(videoId){
    var video_path = "/static/videos/";
    video_path = video_path.concat(videoId, ".mp4");
    console.log(video_path);
    document.getElementById("video_div").innerHTML = '<video id=' + videoId + '_play width="1000" height="750" onclick="playVideo(this.id)" controls> <source src=' + video_path + ' type="video/mp4"> </video>';
    console.log(document.getElementById("video_div"));
}

function playVideo(videoId){
    var name = document.getElementById("username");
    console.log(name.innerHTML);
    if (name.innerHTML == "Enter username."){
        alert("Please enter your user name.");
        return false;
    }
    var status = document.getElementById(videoId).getAttribute("status");
    if (status == null || status=="off"){
        document.getElementById(videoId).setAttribute("status", "on");
        $.get("/video_feed", { id: videoId, username: name.innerHTML });
    }
    else{
        document.getElementById(videoId).setAttribute("status", "off");
        $.get("/video_stop", { id: videoId, username: name.innerHTML });
    }
    console.log("Status: " + document.getElementById(videoId).getAttribute("status"));
}
