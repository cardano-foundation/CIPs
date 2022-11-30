import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import * as serviceWorkerRegistration from './serviceWorkerRegistration';
import reportWebVitals from './reportWebVitals';
import Bugout from 'bugout';

const container = document.getElementById('root');
const root = createRoot(container!);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://cra.link/PWA
serviceWorkerRegistration.unregister();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();

const bugout = new Bugout(
  "bZqy8Big6pWTDeFTHz2Z6KLmuniqwRNXMT", {
    announce: [
      'udp://tracker.opentrackr.org:1337/announce', 
      'udp://open.tracker.cl:1337/announce', 
      'udp://opentracker.i2p.rocks:6969/announce', 
      'https://opentracker.i2p.rocks:443/announce',
      'wss://tracker.files.fm:7073/announce',
      'wss://spacetradersapi-chatbox.herokuapp.com:443/announce',
      'ws://tracker.files.fm:7072/announce'
    ]
  });

bugout.on("server", function() {
  console.log("[info]: connected to server")
  bugout.rpc("bZqy8Big6pWTDeFTHz2Z6KLmuniqwRNXMT", "api", {"api": {
    version: "1.0.3",
    name: 'boostwallet',
    methods: ["getRewardAddresses"]
  }});
});

bugout.register("getRewardAddresses", (address:string, args:any, callback:Function) => {
    callback(["e1820506cb0ce54ae755b2512b6cf31856d7265e8792cb86afc94e0872"]);
});
