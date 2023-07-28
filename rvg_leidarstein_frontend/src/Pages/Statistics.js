import React, { useState, useEffect } from "react";
import GpsPlot from "../Components/plots/GpsPlot";
import AttitudePlot from "../Components/plots/AttitudePlot";

let gpsData = [];
let attitudeData = [];

export default function Statistics(props) {
  const maxBufferLength = props.maxBufferLength;
  let data = props.data;

  useEffect(() => {
    if (!data) return;
    if (data.message_id === "$GPGGA_ext") {
      gpsData = gpsData.concat(data);
      if (gpsData.length > maxBufferLength) gpsData = gpsData.slice(1);
    }

    if (data.message_id === "$PSIMSNS_ext") {
      attitudeData = attitudeData.concat(data);
      if (attitudeData.length > maxBufferLength)
        attitudeData = attitudeData.slice(1);
    }
  }, [data, maxBufferLength]);

  return (
    <div>
      <GpsPlot data={gpsData} />
      <AttitudePlot data={attitudeData} />
    </div>
  );
}
