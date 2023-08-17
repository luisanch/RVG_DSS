import React, { useRef, useState, useEffect } from "react";
import "./DomainCanvas.css";

function DomainCanvas(props) {
  const sendMessage = props.sendMessage;
  const canvasRef = useRef(null);
  const [canvasId, setCanvasId] = useState("SAFE"); // Default canvas ID
  const [canvasLines, setCanvasLines] = useState({
    SAFE: [],
    OVERTAKING_STAR: [],
    OVERTAKING_PORT: [],
    HEADON: [],
    GIVEWAY: [],
    STANDON: [],
  });
  const [previewLine, setPreviewLine] = useState(null);
  const canvasSize = 400;
  const gridFactor = 8;

  const handleCanvasClick = (e) => {
    if (previewLine) {
      const newLine = { ...previewLine };
      setCanvasLines((prevCanvasLines) => ({
        ...prevCanvasLines,
        [canvasId]: [...prevCanvasLines[canvasId], newLine],
      }));
      setPreviewLine(null); // Reset preview line after clicking
    }
  };

  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const newPreviewLine = calculatePerpendicularLine(canvasSize, x, y);
    setPreviewLine(newPreviewLine);
  };

  const handleCanvasLeave = () => {
    setPreviewLine(null); // Reset preview line when mouse leaves canvas
  };

  const handleCanvasEnter = (e) => {
    handleMouseMove(e);
  };

  const calculatePerpendicularLine = (canvasSize, x, y) => {
    const centerX = canvasSize / 2;
    const centerY = canvasSize / 2;
    const length = canvasSize; // Set line length to canvas height

    let endX1 = x;
    let endY1 = y + length;
    let endX2 = x;
    let endY2 = y - length;

    const slope = (centerY - y) / (centerX - x);
    if (slope != 0) {
      const perpendicularSlope = -1 / slope;

      endX1 =
        x + length / Math.sqrt(1 + perpendicularSlope * perpendicularSlope);
      endY1 = y + perpendicularSlope * (endX1 - x);
      endX2 =
        x - length / Math.sqrt(1 + perpendicularSlope * perpendicularSlope);
      endY2 = y - perpendicularSlope * (endX1 - x);
    } 
    return { startX: x, startY: y, endX1, endY1, endX2, endY2 };
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvasSize, canvasSize);
    drawGrid(ctx);
    drawLines(ctx);
    drawPreviewLine(ctx);
    drawCenter(ctx);
  }, [canvasLines[canvasId], previewLine, canvasSize]);

  const drawCenter = (ctx) => {
    const centerX = canvasSize / 2;
    const centerY = canvasSize / 2;
    const crossSize = 10;

    ctx.beginPath();
    ctx.moveTo(centerX - crossSize / 2, centerY);
    ctx.lineTo(centerX + crossSize / 2, centerY);
    ctx.moveTo(centerX, centerY - crossSize / 2);
    ctx.lineTo(centerX, centerY + crossSize / 2);
    ctx.strokeStyle = "red";
    ctx.stroke();
  };

  const drawLines = (ctx) => {
    canvasLines[canvasId].forEach((line, index) => {
      ctx.beginPath();
      ctx.moveTo(line.startX, line.startY);
      ctx.lineTo(line.endX1, line.endY1);
      ctx.moveTo(line.startX, line.startY);
      ctx.lineTo(line.endX2, line.endY2);
      ctx.strokeStyle = "black";
      ctx.stroke();
    });
  };

  const drawPreviewLine = (ctx) => {
    if (previewLine != null) {
      ctx.beginPath();
      ctx.moveTo(previewLine.startX, previewLine.startY);
      ctx.lineTo(previewLine.endX1, previewLine.endY1);
      ctx.moveTo(previewLine.startX, previewLine.startY);
      ctx.lineTo(previewLine.endX2, previewLine.endY2);
      ctx.strokeStyle = "black";
      ctx.stroke();
    }
  };

  const drawGrid = (ctx) => {
    const gridSize = canvasSize / gridFactor;
    const centerX = canvasSize / 2;
    const centerY = canvasSize / 2;
    const gridOriginX =
      centerX % gridSize === 0 ? centerX : centerX - (centerX % gridSize);
    const gridOriginY =
      centerY % gridSize === 0 ? centerY : centerY - (centerY % gridSize);

    ctx.strokeStyle = "#ddd"; // Grid color

    // Draw horizontal grid lines and scale markings
    for (let y = 0; y <= canvasSize; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvasSize, y);
      ctx.stroke();

      // Draw scale marking on the positive y-axis
      if (y !== centerY) {
        const scaleValue = ((centerY - y) / gridSize).toFixed(1);
        ctx.fillText(scaleValue, centerX + 5, y + 10);
      }
    }

    // Draw vertical grid lines and scale markings
    for (let x = 0; x <= canvasSize; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvasSize);
      ctx.stroke();

      // Draw scale marking on the positive x-axis
      if (x !== centerX) {
        const scaleValue = ((x - centerX) / gridSize).toFixed(1);
        ctx.fillText(scaleValue, x + 5, centerY + 15);
      }
    }

    // Draw axes
    ctx.strokeStyle = "#000"; // Axes color
    ctx.beginPath();
    ctx.moveTo(centerX, 0);
    ctx.lineTo(centerX, canvasSize);
    ctx.moveTo(0, centerY);
    ctx.lineTo(canvasSize, centerY);
    ctx.stroke();
  };

  const handleDeleteLastLine = () => {
    if (canvasLines[canvasId].length > 0) {
      const updatedLines = canvasLines[canvasId].slice(
        0,
        canvasLines[canvasId].length - 1
      );
      setCanvasLines((prevCanvasLines) => ({
        ...prevCanvasLines,
        [canvasId]: updatedLines,
      }));
    }
  };

  const handleSave = () => {
    if (canvasLines[canvasId].length > 0) {
      let message = {
        type: "datain",
        content: {
          message_id: "cbf_domains",
        },
      };

      const keys = Object.keys(canvasLines);
      console.log(keys);
      keys.forEach((key) => {
        console.log(key);
        message.content[key] = {};
        message.content[key].d = [];
        message.content[key].z1 = [];
        message.content[key].z2 = [];

        if (canvasLines[key].length > 0) {
          canvasLines[key].forEach((line) => {
            const x =
              (gridFactor * (line.startX - canvasSize / 2)) / canvasSize;
            const y =
              (gridFactor * (canvasSize / 2 - line.startY)) / canvasSize;
            const d = Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2));
            message.content[key].d.push(d);
            message.content[key].z1.push(x / d);
            message.content[key].z2.push(y / d);
          });
        }
      });
      sendMessage(JSON.stringify(message, null, 2));
    }
  };

  return (
    <div className="Container">
      <div className="ControlsRow">
        <button onClick={handleDeleteLastLine} className="Button">
          Delete
        </button>
        <button onClick={handleSave} className="Button">
          Save
        </button>
        <select value={canvasId} onChange={(e) => setCanvasId(e.target.value)}>
          <option value="SAFE">SAFE</option>
          <option value="OVERTAKING_STAR">OVERTAKING_STAR</option>
          <option value="OVERTAKING_PORT">OVERTAKING_PORT</option>
          <option value="HEADON">HEADON</option>
          <option value="GIVEWAY">GIVEWAY</option>
          <option value="STANDON">STANDON</option>
          {/* Add more options for additional canvases */}
        </select>
      </div>
      <canvas
        ref={canvasRef}
        width={canvasSize}
        height={canvasSize}
        onClick={handleCanvasClick}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleCanvasLeave}
        onMouseEnter={handleCanvasEnter}
      ></canvas>
    </div>
  );
}

export default DomainCanvas;
