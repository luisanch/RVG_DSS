import React, { useState, useEffect } from "react";
import Slider from "@mui/material/Slider";
import "./Map.css";

// Function component for rendering control sliders
export default function Controls({ settings, sendMessage }) {
  // State variables to store slider values and showSimControls setting
  const [slider1Value, setSlider1Value] = useState(0);
  const [slider2Value, setSlider2Value] = useState(0);
  const [showSimControls, setShowSimControls] = useState(
    settings.showSimControls
  );

  // useEffect hook to update showSimControls state when settings prop changes
  useEffect(() => {
    if (settings.showSimControls !== showSimControls) {
      setShowSimControls(settings.showSimControls);
    }
  }, [settings.showSimControls, showSimControls]);

  // Event handler for Slider 1 value change
  const handleSlider1Change = (event, newValue) => {
    setSlider1Value(newValue);

    // Create a message object with the updated slider value and send it via Websockets
    const message = {
      type: "datain",
      content: {
        message_id: "control_azi",
        val: newValue,
      },
    };
    sendMessage(JSON.stringify(message, null, 2));
  };

  // Event handler for Slider 2 value change
  const handleSlider2Change = (event, newValue) => {
    setSlider2Value(newValue);
    // Create a message object with the updated slider value and send it via Websockets
    const message = {
      type: "datain",
      content: {
        message_id: "control_thrust",
        val: newValue,
      },
    };
    sendMessage(JSON.stringify(message, null, 2));
  };

  // Conditional rendering of sliders based on showSimControls value
  const controls = showSimControls ? (
    <div className="slider-container">
      <div className="slider-wrapper">
        <div className="slider-label">Azimuth Angle: {slider1Value}</div>
        {/* Slider 1 component with relevant properties */}
        <Slider
          value={slider1Value}
          min={-30}
          max={30}
          onChange={handleSlider1Change}
          aria-labelledby="slider1"
        />
        <div className="slider-label">Thruster Revs: {slider2Value}</div>
        {/* Slider 2 component with relevant properties */}
        <Slider
          value={slider2Value}
          min={0}
          max={300}
          onChange={handleSlider2Change}
          aria-labelledby="slider2"
        />
      </div>
    </div>
  ) : null;

  // Return the controls JSX element
  return controls;
}
