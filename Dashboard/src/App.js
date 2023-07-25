import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Sidenav from "./Components/Sidenav";
import Explore from "./Pages/Explore";
import Home from "./Pages/Home";
import Settings from "./Pages/Settings";
import Statistics from "./Pages/Statistics";
import useWebSocket, { ReadyState } from "react-use-websocket";
import React, { useState, useCallback, useEffect } from "react"; 

const WS_URL = "ws://127.0.0.1:8000";
let messageHistory = [];
// let stampArray = [];
// let timerStart = Date.now()/1000;
// let hourtag = 1;

function App() {
  const nmeaFilters = ["$GPGGA_ext", "$PSIMSNS_ext"];
  const aisFilter = "!AI";
  const colavFilter = "arpa";
  const cbfFilter = "cbf";
  const maxBufferLength = 60;
  // const saveInterval = 3600;
  const [settings, setSettings] = useState({
    showHitbox: true,
    showAllTooltips: true,
    shortTooltips: true,
    showDebugOverlay: false,
    navigationMode: false,
    showSimControls: false,
    simMode: "4dof",
  });

  const { sendMessage, lastMessage, readyState } = useWebSocket(WS_URL, {
    share: true,
    filter: isDataIn,
  });

  function isDataIn(message) {
    let evt = JSON.parse(message.data);
    return evt.type === "datain";
  }

  useEffect(() => {
    if (lastMessage !== null) {
      let newMsg = parseDataIn(lastMessage.data);
      if (newMsg === null) return;
      messageHistory.push(newMsg);
      if (messageHistory.length > maxBufferLength) {
        messageHistory.shift();
      }
    }
  }, [lastMessage, messageHistory]);

  function parseDataIn(msgString) {
    const msg = JSON.parse(msgString).data;

    if (
      nmeaFilters.includes(msg.message_id) ||
      (msg.message_id.includes(aisFilter) && msg.message_id.includes("_ext")) ||
      msg.message_id.includes(colavFilter) ||
      msg.message_id.includes(cbfFilter)
    ) {
      // const currDate = Date.now() / 1000;
      // if (currDate > (timerStart + saveInterval)) {
      //   const logname = "hour" + hourtag + "log"
      //   localStorage.setItem(logname, JSON.stringify(stampArray, null, 2))
      //   hourtag++
      //   stampArray = []
      //   timerStart = Date.now() / 1000
      //   console.log("new log saved")
      // } else {
      //   stampArray.push(Date.now() / 1000 - msg.unix_time)
      // }
      return msg;
    } else {
      return null;
    }
  }

  const connectionStatus = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  }[readyState];

  return (
    <div className="App">
      <Sidenav />
      <main>
        <Routes>
          <Route
            path="/"
            element={
              <Home
                settings={settings}
                sendMessage={sendMessage}
                data={messageHistory[messageHistory.length - 1]}
              />
            }
          />
          <Route path="/explore" element={<Explore />} />
          <Route
            path="/statistics"
            element={
              <Statistics
                data={messageHistory[messageHistory.length - 1]}
                maxBufferLength={maxBufferLength}
              />
            }
          />
          <Route
            path="/settings"
            element={<Settings settings={settings} setSettings={setSettings} sendMessage={sendMessage}/>}
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
