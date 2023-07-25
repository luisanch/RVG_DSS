import React, { useState, useCallback, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const AttitudePlot = (props) => {
  const data = props.data;

  return (
    <table>
      <tr>
        <td>
          <LineChart
            data={data}
            width={500}
            height={300}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" angle={45} y={10} />
            <YAxis type="number" domain={["0", "360"]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="head_deg" stroke="#8884d8" />
          </LineChart>
        </td>
        <td>
          <LineChart
            data={data}
            width={500}
            height={300}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" angle={45} />
            <YAxis domain={["dataMin", "datamax"]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="pitch_deg" stroke="#8884d8" />
          </LineChart>
        </td>
        <td>
          <LineChart
            data={data}
            width={500}
            height={300}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" angle={45} />
            <YAxis domain={["dataMin", "datamax"]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="roll_deg" stroke="#8884d8" />
          </LineChart>
        </td>
      </tr>
    </table>
  );
};

export default AttitudePlot;
