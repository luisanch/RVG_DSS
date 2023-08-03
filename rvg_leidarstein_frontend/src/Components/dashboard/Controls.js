import React, { useState, useEffect } from "react";
import Slider from "@mui/material/Slider";
import "./Map.css";

export default function Controls({settings, sendMessage}) {
  const [slider1Value, setSlider1Value] = useState(0);
  const [slider2Value, setSlider2Value] = useState(0);
  const [showSimControls, setShowSimControls] = useState(
    settings.showSimControls
  );

  useEffect(() => {
if (settings.showSimControls != showSimControls) {
setShowSimControls(settings.showSimControls)
}
  });

  const handleSlider1Change = (event, newValue) => {
    setSlider1Value(newValue);
    const message = {
      type: "datain",
      content: {
        message_id: "control_azi",
        val: newValue,
      },
    };
    sendMessage(JSON.stringify(message, null, 2));
  };

  const handleSlider2Change = (event, newValue) => {
    setSlider2Value(newValue);
    const message = {
      type: "datain",
      content: {
        message_id: "control_thrust",
        val: newValue,
      },
    };
    sendMessage(JSON.stringify(message, null, 2));
  };

  const controls = showSimControls ? (
    <div className="slider-container">
      <div className="slider-wrapper">
        <div className="slider-label">Azimuth Angle: {slider1Value}</div>
        <Slider
          value={slider1Value}
          min={-30}
          max={30}
          onChange={handleSlider1Change}
          aria-labelledby="slider1"
        />
        <div className="slider-label">Thruster Revs: {slider2Value}</div>
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

  return controls;
}
