const CLOSED = 3;


export default class WS {
    /**
     * Websocket server wrapper.
     * Perform auto-reconnect in case of lost connectivity
     * @param url: websocket url
     * @param onmessage: message handler
     */
    constructor(url, onmessage) {

        this.url = url;
        this.onmessage = onmessage;
        this.reconnectInterval = null;
        this.initServer();

    }

    initServer() {
        console.log("init websocket server");
        this.server = new WebSocket(this.url);
        this.server.onmessage = this.onmessage;
        this.server.onopen = () => this.server.send(
            JSON.stringify({
                type: "init"
            }));

        this.initReconnect()
    }

    initReconnect() {

        let self = this;

        if (this.reconnectInterval) {
            // clear previous interval
            console.log("clear websocket reconnect interval");
            clearInterval(this.reconnectInterval);
        }

        this.reconnectInterval = setInterval(function () {
            if (self.server.readyState === CLOSED) {
                console.log("websocket connection closed. trying to re-connect");
                self.initServer()
            }
        }, 5000);

    }

}
