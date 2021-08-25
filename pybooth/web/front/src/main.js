const body =  document.getElementsByTagName("body")[0];
let ws = null;
const urls = [];
let createdImageTags = 0;
let nextImageCursor = 0;
const maxImageTags = 4;
let socketReconnectInterval = null;

const eventHandlers = new Map([
    [
        "WEB_INIT", (data) => {
            clearImageTags();
            urls.splice(0, urls.length)
            for (let pic of data.pics) {
                url = window.origin + "/pictures/" + pic
                urls.push(url)
                createImageTag(url)
            }
        },
    ],
    [
        "COMPOSITION_CREATED", ({path}) => {
            url = window.origin + "/pictures/" + path.split("/").reverse()[0]
            urls.push(url)
            createImageTag(url)
            displayImagePopin(url)
        }
    ],
    [
        "CAPTURE_COUNTDOWN", ({timeout}) => {
            const overlay = document.createElement("div");
            overlay.classList = ["new-picture-overlay"];
            const h1 = document.createElement("h1")
            h1.innerText = "SAY CHEESE"
            overlay.appendChild(h1)
            body.appendChild(overlay);
            setTimeout(() => {body.removeChild(overlay)}, timeout * 1000);
        }
    ]
])

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

function clearImageTags() {
    createdImageTags = 0;
    nextImageCursor = 0;
    const tags = Array.from(document.getElementsByClassName("booth-composition"))
    for (const tag of tags) {
        tag.parentNode.removeChild(tag);
        console.log(tag);
    }
}

function createImageTag(url) {
    const img = document.createElement("img");
    img.src = getNextImage();
    img.classList = ["booth-composition"];
    body.appendChild(img);
    createdImageTags++;
    if (createdImageTags >= maxImageTags) {
        setTimeout(slide, 1000);
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
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    ws.onmessage = function(raw) {
        const msg = JSON.parse(raw.data);
        const handler = eventHandlers.get(msg.event);
        if (!handler) return;
        handler(msg.data)
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
