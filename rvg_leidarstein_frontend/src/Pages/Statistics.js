/**
 * A React component representing the statistics dashboard for GPS and attitude data.
 * It receives real-time data updates through props and displays them using two separate plots:
 * - A GPS plot to visualize GPS data.
 * - An attitude plot to visualize attitude data.
 *
 * @param {object} props - The props object that contains the following properties:
 *   @param {number} maxBufferLength - The maximum number of data points to be stored in the buffer.
 *   @param {object} data - The real-time data object containing GPS and attitude data points.
 *
 * @returns {JSX.Element} - Returns a JSX element containing the GPS and attitude plots.
 */
import React, { useState, useEffect } from "react";
import GpsPlot from "../Components/plots/GpsPlot";
import AttitudePlot from "../Components/plots/AttitudePlot";

// Initialize empty arrays to store GPS and attitude data
let gpsData = [];
let attitudeData = [];

export default function Statistics(props) {
  // Extracting props
  const maxBufferLength = props.maxBufferLength;
  let data = props.data;

  // Effect hook to update GPS and attitude data arrays whenever new data is received
  useEffect(() => {
    if (!data) return;
    // Check the message_id to determine the type of data (GPS or attitude)
    if (data.message_id === "$GPGGA_ext") {
      gpsData = gpsData.concat(data);
      // Keep the buffer size limited to maxBufferLength
      if (gpsData.length > maxBufferLength) gpsData = gpsData.slice(1);
    }

    if (data.message_id === "$PSIMSNS_ext") {
      attitudeData = attitudeData.concat(data);
      // Keep the buffer size limited to maxBufferLength
      if (attitudeData.length > maxBufferLength)
        attitudeData = attitudeData.slice(1);
    }
  }, [data, maxBufferLength]);

  return (
    <div>
      {/* Render the GPS and attitude plots with the updated data */}
      <GpsPlot data={gpsData} />
      <AttitudePlot data={attitudeData} />
    </div>
  );
}
