import React, { useRef, useState, useEffect } from "react";
import "./DomainCanvas.css";

function DomainCanvas() {
  const canvasRef = useRef(null);
  const [lines, setLines] = useState([]);
  const [previewLine, setPreviewLine] = useState(null);
  const canvasSize = 500;

  const handleCanvasClick = (e) => {
    if (previewLine) {
      const newLine = { ...previewLine };
      setLines([...lines, newLine]);
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
    drawPreviewLine(ctx);
  }, [lines, previewLine, canvasSize]);

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

  const handleDeleteLastLine = () => {
    if (lines.length > 0) {
      const updatedLines = lines.slice(0, lines.length - 1);
      setLines(updatedLines);
    }
  };

  return (
    <div className="Container">
      <button onClick={handleDeleteLastLine} className="DeleteButton">
        Delete
      </button>
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
