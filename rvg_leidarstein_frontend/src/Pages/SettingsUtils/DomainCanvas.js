import React, { useRef, useState, useEffect } from "react";
import "./DomainCanvas.css";

function DomainCanvas() {
  const canvasRef = useRef(null);
  const [lines, setLines] = useState([]);
  const canvasSize = 500;

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newLine = calculatePerpendicularLine(canvasSize, x, y);
    setLines([...lines, newLine]);
  };

  const calculatePerpendicularLine = (canvasSize, x, y) => {
    const centerX = canvasSize / 2;
    const centerY = canvasSize / 2;

    const slope = (centerY - y) / (centerX - x);
    const perpendicularSlope = -1 / slope;

    const length = canvasSize / 2; // Set line length to canvas height
    const endX1 =
      x + length / Math.sqrt(1 + perpendicularSlope * perpendicularSlope);
    const endY1 = y + perpendicularSlope * (endX1 - x);
    const endX2 =
      x - length / Math.sqrt(1 + perpendicularSlope * perpendicularSlope);
    const endY2 = y - perpendicularSlope * (endX1 - x);

    return { startX: x, startY: y, endX1, endY1, endX2, endY2 };
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvasSize, canvasSize);
    drawCenter(ctx);
    drawLines(ctx);
  }, [lines, canvasSize]);

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
    lines.forEach((line, index) => {
      ctx.beginPath();
      ctx.moveTo(line.startX, line.startY);
      ctx.lineTo(line.endX1, line.endY1);
      ctx.moveTo(line.startX, line.startY);
      ctx.lineTo(line.endX2, line.endY2);
      ctx.strokeStyle = "black";
      ctx.stroke();
    });
  };

  const handleDeleteLastLine = () => {
    if (lines.length > 0) {
      const updatedLines = lines.slice(0, lines.length - 1);
      setLines(updatedLines);
    }
  };

  return (
    <div className="Container">
      <button onClick={handleDeleteLastLine} className="DeleteButton">
        Delete Last Line
      </button>
      <canvas
        ref={canvasRef}
        width={canvasSize}
        height={canvasSize}
        onClick={handleCanvasClick}
      ></canvas>
    </div>
  );
}

export default DomainCanvas;
