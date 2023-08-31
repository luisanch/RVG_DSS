// Import necessary dependencies
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Sidenav from "./Components/Sidenav";
import Home from "./Pages/Home";
import Settings from "./Pages/Settings";
import Statistics from "./Pages/Statistics";
import useWebSocket, { ReadyState } from "react-use-websocket";
import React, { useState, useCallback, useEffect } from "react";

// WebSocket URL
const WS_URL = "ws://127.0.0.1:8000";
// Array to store the received WebSocket messages
let messageHistory = [];

/**
 * The main application component that handles routing and WebSocket communication.
 *
 * @returns {JSX.Element} - A React element containing the main application UI.
 */
function App() {
  // Filters to process WebSocket data
  const nmeaFilters = ["$GPGGA", "$PSIMSNS"];
  const aisFilter = "!";
  const colavFilter = "arpa";
  const cbfFilter = "cbf";
  const encounterFilter = "encounters";
  const maxBufferLength = 60;

  // State to manage application settings
  const [settings, setSettings] = useState({
    showHitbox: true,
    showAllTooltips: false,
    shortTooltips: true,
    navigationMode: false,
    showSimControls: false,
    simMode: "rt",
    showDomains: true,
  });

  // WebSocket connection using react-use-websocket hook
  const { sendMessage, lastMessage, readyState } = useWebSocket(WS_URL, {
    share: true,
    filter: isDataIn,
  });

  /**
   * A callback function to filter WebSocket messages based on the type.
   *
   * @param {MessageEvent} message - The WebSocket message event.
   * @returns {boolean} - True if the message type is "datain", otherwise false.
   */
  function isDataIn(message) {
    let evt = JSON.parse(message.data);
    return evt.type === "datain";
  }

  // Effect hook to process incoming WebSocket messages
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

  /**
   * Parse the incoming "datain" WebSocket message and apply filters.
   *
   * @param {string} msgString - The incoming WebSocket message string.
   * @returns {object|null} - The parsed message object if it matches the filters, otherwise null.
   */
  function parseDataIn(msgString) {
    const msg = JSON.parse(msgString).content; 
    if (
      nmeaFilters.includes(msg.message_id) ||
      msg.message_id.includes(aisFilter) ||
      msg.message_id.includes(colavFilter) ||
      msg.message_id.includes(cbfFilter) ||
      msg.message_id.includes(encounterFilter)
    ) {
      return msg;
    } else {
      return null;
    }
  }

  // Connection status text based on the WebSocket connection state
  const connectionStatus = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  }[readyState];

  // Render the main application UI
  return (
    <div className="App">
      {/* Sidebar navigation component */}
      <Sidenav />
      <main>
        {/* React Router for handling different routes */}
        <Routes>
          {/* Home page */}
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
          {/* Statistics page */}
          <Route
            path="/statistics"
            element={
              <Statistics
                data={messageHistory[messageHistory.length - 1]}
                maxBufferLength={maxBufferLength}
              />
            }
          />
          {/* Settings page */}
          <Route
            path="/settings"
            element={
              <Settings
                settings={settings}
                setSettings={setSettings}
                sendMessage={sendMessage}
              />
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
