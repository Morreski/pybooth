const body =  document.getElementsByTagName("body")[0];
let ws = null;
let firstImageBatchReceived = false;
const urls = [];
let createdImageTags = 0;
let nextImageCursor = 0;
const maxImageTags = 4;
let socketReconnectInterval = null;

function getNextImage() {
    if (nextImageCursor >= urls.length) {
        nextImageCursor = 0;
    }
    return urls[nextImageCursor++];
}

function slide() {
    let img = document.getElementsByTagName("img")[0];
    img.addEventListener("transitionend", onImageLeave);
    img.style.marginLeft = "-33%";
}

function onImageLeave(evt) {
    body.removeChild(evt.target);
    body.appendChild(evt.target);
    evt.target.removeEventListener("transitionend", onImageLeave);
    evt.target.style.marginLeft = "";
    evt.target.src = getNextImage();
    slide();
}

function createImageTag(url) {
    const img = document.createElement("img");
    img.src = getNextImage();
    body.appendChild(img);
    createdImageTags++;
    if (createdImageTags >= maxImageTags) {
        setTimeout(slide, 1000);
    }
}

function onNewImage(url) {
    if (createdImageTags < maxImageTags) {
        createImageTag(url)
    }
    if (firstImageBatchReceived) {
        displayImagePopin(url)
    }
}

function displayImagePopin(url) {

    const overlay = document.createElement("div");
    overlay.classList = ["new-picture-overlay"];
    const img = document.createElement("img");
    img.src = url;
    overlay.appendChild(img);
    body.appendChild(overlay);
    setTimeout(() => {body.removeChild(overlay)}, 10000);
}

function connectWebSocket(force) {
    if (socketReconnectInterval != null) {
        clearInterval(socketReconnectInterval);
    } else if (! force) {
        // There is already a reconnect loop running
        return
    }
    ws = new WebSocket(`ws://${window.location.host}/pictures`);
    ws.onmessage = function(msg) {
        for (let imgName of JSON.parse(msg.data)) {
            url = window.origin + "/pictures/" + imgName
            urls.push(url)
            onNewImage(url)
        }
        firstImageBatchReceived = true;
    }

    ws.onopen = function() {
        socketReconnectInterval = null;
    }

    ws.onclose = function() {
        console.error("Websocket disconnected");
        socketReconnectInterval = setInterval(connectWebSocket.bind(false), 3000)
    }
}

connectWebSocket(true)
