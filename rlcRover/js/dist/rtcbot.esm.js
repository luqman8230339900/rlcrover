// We want the library to work in node too, but it doesn't contain webrtc!
// We therefore conditionally require wrtc.
const _RTCPeerConnection =
  typeof RTCPeerConnection != "undefined"
    ? RTCPeerConnection
    : require("wrtc").RTCPeerConnection;

class ConnectionStreamHandler {
  constructor(rtc) {
    this._callback = null;

    // The incoming and outgoing data streams
    this.incomingStream = null;
    this.outgoingStream = null;

    this._rtc = rtc;
    this._offerToReceive = false;
  }

  subscribe(f) {
    this._callback = f;

    // Since we subscribe to a video stream, we offer to receive one.
    this.offerToReceive();
  }

  putSubscription(track) {
    this.outgoingStream = track;
    this._rtc.addTrack(track);
  }

  offerToReceive() {
    this._offerToReceive = true;
  }

  _onTrack(track) {
    // This is the internal track receiver. Right now only supports a single incoming stream.
    this.incomingStream = track.streams[0];
    if (this._callback != null) {
      this._callback(track.streams[0]);
    }
  }
}

class RTCConnection {
  /**
   * RTCConnection mirrors the Python RTCConnection in API. Whatever differences in functionality
   * that may exist can be considered bugs unless explictly documented as such.
   *
   * For detailed documentation, see the RTCConnection docs for Python.
   *
   * @param {*} defaultOrdered
   * @param {*} rtcConfiguration is the configuration given to the RTC connection
   */
  constructor(
    defaultOrdered = true,
    rtcConfiguration = {
      iceServers: [{ urls: ["stun:stun.l.google.com:19302"] }]
    }
  ) {
    this._dataChannels = {};

    this._msgcallback = msg => console.log(msg);

    this._rtc = new _RTCPeerConnection(rtcConfiguration);
    this._rtc.ondatachannel = this._onDataChannel.bind(this);
    this._rtc.ontrack = this._onTrack.bind(this);

    /**
     * Just like in the Python version, the video element allows you to directly access video streams.
     * The following functions are available:
     *
     * - `subscribe()`: Unlike in Python, this is given a callback which is called *once*, when the stream
     *  is received.
     *
     *  .. code-block:: javascript
     *
     *    conn.video.subscribe(function(stream) {
     *      document.querySelector("video").srcObject = stream;
     *    });
     *
     * - `putSubscription()`: Allows to send a video stream:
     *
     *  .. code-block:: javascript
     *
     *    let streams = await navigator.mediaDevices.getUserMedia({audio: false, video: true});
     *    conn.video.putSubscription(streams.getVideoTracks()[0]);
     *
     *
     */
    this.video = new ConnectionStreamHandler(this._rtc);
    /**
     * The audio element allows you to directly access audio streams.
     * The following functions are available:
     *
     * - `subscribe()`: Unlike in Python, this is given a callback which is called *once*, when the stream
     *  is received.
     *
     *  .. code-block:: javascript
     *
     *    conn.audio.subscribe(function(stream) {
     *      document.querySelector("audio").srcObject = stream;
     *    });
     *
     * - `putSubscription()`: Allows to send a video stream:
     *
     *  .. code-block:: javascript
     *
     *    let streams = await navigator.mediaDevices.getUserMedia({audio: true, video: false});
     *    conn.audio.putSubscription(streams.getAudioTracks()[0]);
     *
     *
     */
    this.audio = new ConnectionStreamHandler(this._rtc);

    this._hasRemoteDescription = false;
    this._defaultChannel = null;
    this._defaultOrdered = defaultOrdered;
    this.__queuedMessages = [];

    // Bind the put_nowait method
    this.put_nowait = this.put_nowait.bind(this);
  }

  async _waitForICECandidates() {
    // https://muaz-khan.blogspot.com/2015/01/disable-ice-trickling.html
    const conn = this._rtc;
    // Waits until the connection has finished gathering ICE candidates
    await new Promise(function(resolve) {
      if (conn.iceGatheringState === "complete") {
        resolve();
      } else {
        function checkState() {
          if (conn.iceGatheringState === "complete") {
            conn.removeEventListener("icegatheringstatechange", checkState);
            resolve();
          }
        }
        conn.addEventListener("icegatheringstatechange", checkState);
      }
    });
  }
  /**
   * Sets up the connection. If no description is passed in, creates an initial description.
   * If a description is given, creates a response to it.
   * @param {*} description (optional)
   */
  async getLocalDescription(description = null) {
    /**
     * Gets the description
     */

    if (this._hasRemoteDescription || description != null) {
      // This means that we received an offer - either the remote description
      // was already set, or we were passed in a description. In either case,
      // instead of initializing a new connection, we prepare a response
      if (!this._hasRemoteDescription) {
        await this.setRemoteDescription(description);
      }
      let answer = await this._rtc.createAnswer();
      await this._rtc.setLocalDescription(answer);
      await this._waitForICECandidates();
      return {
        sdp: this._rtc.localDescription.sdp,
        type: this._rtc.localDescription.type
      };
    }

    // There was no remote description, which means that we are intitializing
    // the connection.

    // Before starting init, we create a default data channel for the connection
    this._defaultChannel = this._rtc.createDataChannel("default", {
      ordered: this._defaultOrdered
    });
    this._defaultChannel.onmessage = this._onMessage.bind(
      this,
      this._defaultChannel
    );
    this._defaultChannel.onopen = this._sendQueuedMessages.bind(this);

    let offer = await this._rtc.createOffer({
      offerToReceiveVideo: this.video._offerToReceive,
      offerToReceiveAudio: this.audio._offerToReceive
    });
    await this._rtc.setLocalDescription(offer);
    // For simplicity of the API, we wait until all ICE candidates are
    // ready before trying to connect, instead of doing asynchronous signaling.
    await this._waitForICECandidates();
    return this._rtc.localDescription;
  }
  /**
   * When initializing a connection, this response reads the remote response to an initial
   * description.
   * 
   * @param {*} description
   */
  async setRemoteDescription(description) {
    await this._rtc.setRemoteDescription(description);
    this._hasRemoteDescription = true;
  }

  _sendQueuedMessages() {
    //console.log("sending queued messages", this.__queuedMessages);
    if (this.__queuedMessages.length > 0) {
      for (let i = 0; i < this.__queuedMessages.length; i++) {
        //console.log("Sending", this.__queuedMessages[i]);
        this._defaultChannel.send(this.__queuedMessages[i]);
      }
      this.__queuedMessages = [];
    }
  }

  _onDataChannel(channel) {
    console.log(channel);
    channel = channel.channel;
    channel.onmessage = this._onMessage.bind(this, channel);
    if (channel.label == "default") {
      //console.log("Got default channel");
      this._defaultChannel = channel;
      channel.onopen = () => this._sendQueuedMessages();
    } else {
      channel.onopen = () => (this._dataChannels[channel.label] = channel);
    }
  }
  _onTrack(track) {
    //console.log("got track", track);
    switch (track.track.kind) {
      case "video":
        this.video._onTrack(track);
        break;
      case "audio":
        this.audio._onTrack(track);
        break;
      default:
        console.error("Could not recognize track!");
    }
  }
  _onMessage(channel, message) {
    //console.log("got message", message);
    this._msgcallback(message.data);
  }
  /**
   * Subscribe to incoming messages. Unlike in the Python libary, which can accept
   * a wide variety of inputs, the `subscribe` function in javascript only allows simple
   * callbacks.
   *
   * @param {*} s A function to call each time a new message comes in
   */
  subscribe(callback) {
    this._msgcallback = callback;
  }
  /**
   * Send the given data over a data stream.
   *
   * @param {*} msg - Message to send
   */
  put_nowait(msg) {
    if (typeof msg !== "string") {
      msg = JSON.stringify(msg);
    }
    if (
      this._defaultChannel != null &&
      this._defaultChannel.readyState == "open" &&
      this.__queuedMessages.length == 0
    ) {
      //console.log("Sending directly");
      this._defaultChannel.send(msg);
    } else {
      //console.log("queueing");
      this.__queuedMessages.push(msg);
    }
  }
  /**
   * Close the connection
   */
  async close() {
    for (let chan in this._dataChannels) {
      chan.close();
    }
    if (this._defaultChannel != null) {
      this._defaultChannel.close();
    }
    await this._rtc.close();
  }
}

class Websocket {
  constructor(url) {
    this._subscription = console.log;
    this._ws = WebSocket(url);
    this._ws.onmessage = this._onMessage;
    this._ws.onopen = this._onopen;
    this._msgQueue = [];
  }

  _onMessage(msg) {
    this._subscription(msg);
  }
  _onopen() {
    console.log("opened websocket");
    for (let i = 0; i < this._msgQueue.length; i++) {
      this._ws.send(this._msgQueue[i]);
    }
    this._msgQueue = [];
  }
  put_nowait(msg) {
    if (typeof msg !== "string") {
      msg = JSON.stringify(msg);
    }
    if (this._ws.readyState != 1 || this._msgQueue.length > 0) {
      // The connection is not yet ready - add to the queue
      this._msgQueue.push(msg);
    } else {
      this._ws.send(msg);
    }
  }
  subscribe(s) {
    this._subscription = s;
  }
  close() {
    this._ws.close();
  }
}

class Keyboard {
  /**
   * Keyboard subscribes to keypresses on the keyboard. Internally, the `keydown` and `keyup`
   * events are used to get keys.
   *
   * .. code-block:: javascript
   *
   *  var kb = new rtcbot.Keyboard();
   *  kb.subscribe(function(event) {
   *    console.log(event); // prints the button and joystick events
   *  })
   */
  constructor() {
    this._de = this._downEvent.bind(this);
    this._ue = this._upEvent.bind(this);
    window.addEventListener("keydown", this._de);
    window.addEventListener("keyup", this._ue);
    this._subscription = console.log;
  }
  _downEvent(e) {
    if (!e.repeat) {
      this._subscription({
        type: e.type,
        altKey: e.altKey,
        shiftKey: e.shiftKey,
        keyCode: e.keyCode,
        key: e.key,
        timestamp: e.timestamp
      });
    }
    e.preventDefault();
  }
  _upEvent(e) {
    this._subscription({
      type: e.type,
      altKey: e.altKey,
      shiftKey: e.shiftKey,
      keyCode: e.keyCode,
      key: e.key,
      timestamp: e.timestamp
    });
    e.preventDefault();
  }
  /**
   * Subscribe to the events. Unlike in the Python libary, which can accept
   * a wide variety of inputs, the `subscribe` function in javascript only allows simple
   * callbacks.
   *
   * @param {*} s A function to call on each event
   */
  subscribe(s) {
    this._subscription = s;
  }
  /**
   * Stop listening to keypresses
   */
  close() {
    window.removeEventListener("keydown", this._de);
    window.removeEventListener("keyup", this._ue);
  }
}

/**
 * The gamepad API is pretty weird - we use a global handler loop to get data from all gamepads at once
 */
class GamepadHandler {
  constructor() {
    // The active gamepads
    this._gamepads = [];
    this._prev = []; // Previous gamepad state
    this._interval = null;
    this._mswait = 100;
  }
  loop() {
    let cur = navigator.getGamepads();
    let len = cur.length;
    if (this._gamepads.length < len) {
      len = this._gamepads.length;
    }
    if (this._prev.length < len) {
      len = this._prev.length;
    }
    //console.log(len, this._prev, cur, this._gamepads);
    for (let i = 0; i < len; i++) {
      if (
        this._prev[i] != null &&
        this._gamepads[i] != null &&
        cur[i] != null
      ) {
        // All 3 exist, so we can compare, and send events.

        // Set the full gamepad state
        this._gamepads[i].state = cur[i];

        for (let j = 0; j < cur[i].buttons.length; j++) {
          if (this._prev[i].buttons[j].pressed != cur[i].buttons[j].pressed) {
            this._gamepads[i]._subscription({
              value: cur[i].buttons[j].pressed,
              type: "btn" + j.toString()
            });
          }
        }
        for (let j = 0; j < cur[i].axes.length; j++) {
          if (this._prev[i].axes[j] != cur[i].axes[j]) {
            this._gamepads[i]._subscription({
              value: cur[i].axes[j],
              type: "axis" + j.toString()
            });
          }
        }
      }
    }
    this._prev = cur;
  }
  init() {
    let shouldLoop = false;
    for (let i = 0; i < this._gamepads.length; i++) {
      if (this._gamepads[i] != null) {
        shouldLoop = true;
        break;
      }
    }
    if (shouldLoop && this._interval == null) {
      //console.log("Starting gamepad loop");
      this._interval = setInterval(this.loop.bind(this), this._mswait);
    } else if (!shouldLoop && this._interval != null) {
      //console.log("Stopping gamepad loop");
      clearInterval(this._interval);
      this._interval = null;
    }
  }
  addGamepad(gp) {
    // Takes the first null spot, or adds to the end
    for (let i = 0; i < this._gamepads.length; i++) {
      if (this._gamepads[i] == null) {
        this._gamepads[i] = gp;
        this.init();
        return;
      }
    }
    this._gamepads.push(gp);
    this.init();
  }
  removeGamepad(gp) {
    for (let i = 0; i < this._gamepads.length; i++) {
      if (gp == this._gamepads[i]) {
        this._gamepads[i] = null;
        return;
      }
    }
  }
}

var gamepadHandler = new GamepadHandler();

/**
 * Gamepads are polled at 10Hz by default, so that when moving joystick axes
 * a connection is not immediately flooded with every miniscule joystick change.
 * To modify this behavior, you can set the rate in Hz, allowing lower latency,
 * with the downside of potentially lots of data suddenly overwhelming a connection.
 *
 * @param {number} rate Rate at which gamepad is polled in Hz
 */
function setGamepadRate(rate) {
  gamepadHandler._mswait = Math.round(1000 / rate);
  if (gamepadHandler._interval != null) {
    // If it is already running, reset it
    clearInterval(gamepadHandler._interval);
    gamepadHandler._interval = null;
  }
  gamepadHandler.init();
}


class Gamepad {
  /**
   * Gamepad allows you to use an Xbox controller. It uses the browser Gamepad API,
   * polling at 10Hz by default. Use `rtcbot.setGamepadRate` to change polling frequency.
   *
   * You must plug in the gamepad, and press a button on it for it to be recognized by the browser:
   *
   * .. code-block:: javascript
   *
   *  var gp = new rtcbot.Gamepad();
   *  gp.subscribe(function(event) {
   *    console.log(event); // prints the button and joystick events
   *  })
   */
  constructor() {
    this._subscription = console.log;
    gamepadHandler.addGamepad(this);

    this.state = null;
  }
  /**
   * Subscribe to the events. Unlike in the Python libary, which can accept
   * a wide variety of inputs, the `subscribe` function in javascript only allows simple
   * callbacks.
   *
   * @param {*} s A function to call on each event
   */
  subscribe(s) {
    this._subscription = s;
  }
  /**
   * Stop polling the gamepad.
   */
  close() {
    gamepadHandler.removeGamepad(this);
  }
}

class Queue {
  /**
   * A simple async queue. Useful for converting callbacks into async operations.
   * The API imitates Python's asyncio.Queue, making it easy to avoid callback hell
   */
  constructor() {
    this._waiting = [];
    this._enqueued = [];
  }
  /**
   * Works just like in Python - you put an element on here, and await get to retrieve it
   * @param {*} elem
   */
  put_nowait(elem) {
    this._enqueued.push(elem);
    if (this._waiting.length > 0) {
      this._waiting.shift()(this._enqueued.shift());
    }
  }
  /**
   * get is a coroutine, to be used with await - it returns elements one at a time.
   */
  async get() {
    if (this._enqueued.length > 0) {
      return this._enqueued.shift();
    }
    let tempthis = this;
    return new Promise(function(resolve, reject) {
      tempthis._waiting.push(resolve);
    });
  }
}

export { Gamepad, Keyboard, Queue, RTCConnection, Websocket, setGamepadRate };
