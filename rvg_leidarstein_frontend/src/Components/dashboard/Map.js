import React, { useEffect, useState } from "react";
import { Map, Marker, Overlay, GeoJson, Draggable } from "pigeon-maps";
import getMarkers from "./Markers";
import getArpa from "./Arpa";
import getPaths from "./Paths";
import getCourses from "./Courses";
import getTooltips from "./Tooltips";
import "./Map.css";
import gunnerus from "../../Assets/ships/gunnerus.svg";
import boat from "../../Assets/ships/boat.svg";

import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Slider from "@mui/material/Slider";
import Paper from "@mui/material/Paper";

const aisObject = {};
let countdown = -1;
const refreshInterval = 500;
const cleanupInterval = 15000;
let cleanupCoundownARPA = cleanupInterval;
let cleanupCoundownCBF = cleanupInterval;

// This definitely needs to be broken up into smaller components.
// Pigeonmaps has a tendency to complain about wrapping components.

const MyMap = (props) => {
  const data = props.data;
  const sendMessage = props.sendMessage;
  const markerSize = 20;
  const settings = props.settings;

  const [mapCenter, setMapCenter] = useState([63.43463, 10.39744]);
  const [gunnerusHeading, setGunnerusHeading] = useState(0);
  const [aisData, setAisData] = useState([]);
  const [anchor, setAnchor] = useState([63.43463, 10.39744]);
  const [tipText, setTipText] = useState("");
  const [arpaObject, setArpaObject] = useState([]);
  const [cbfObject, setCBFObject] = useState([]);
  const [zoomScale, setZoomScale] = useState(1);
  const [cbfTimer, setCbftimer] = useState();
  const [slider1Value, setSlider1Value] = useState(0);
  const [slider2Value, setSlider2Value] = useState(0);

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

  const handleZoomLevel = (event) => {
    const scale = event.zoom / (2 * 18);
    // console.log(scale);
    setZoomScale(scale);
  };

  const deg2dec = (coord, direction) => {
    let dir = 1;
    if (direction === "S" || direction === "W") dir = -1;
    let deg = Math.trunc(coord / 100);
    let dec = (coord / 100 - deg) * (10 / 6);
    return dir * (deg + dec);
  };

  const getGeoLine = (points) => {
    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: {
            type: "LineString",
            coordinates: points,
          },
          properties: { prop0: "value0" },
        },
      ],
    };
  };

  const getGeoCircle = (geoCircle) => {
    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: {
            type: "Polygon",
            coordinates: geoCircle,
          },
          properties: { prop0: "value0" },
        },
      ],
    };
  };

  useEffect(() => {
    if (!data) return;
    if (data.message_id === "$GPGGA_ext") {
      const lon = data.lon;
      const lon_dir = data.lon_dir;
      const lat = data.lat;
      const lat_dir = data.lat_dir;
      const res = [deg2dec(lat, lat_dir), deg2dec(lon, lon_dir)];
      setMapCenter(res);
      setAnchor(res);
    }

    if (data.message_id === "$PSIMSNS_ext") {
      setGunnerusHeading(data.head_deg);
    }

    if (data.message_id.indexOf("!AI") === 0) {
      if (!aisObject.hasOwnProperty(data.mmsi)) {
        aisObject[data.mmsi] = data;
        aisObject[data.mmsi]["pinTooltip"] = false;
        aisObject[data.mmsi]["hoverTooltip"] = false;
      } else {
        data["pinTooltip"] = aisObject[data.mmsi]["pinTooltip"];
        data["hoverTooltip"] = aisObject[data.mmsi]["hoverTooltip"];
        aisObject[data.mmsi] = data;
      }
    }

    if (data.message_id.indexOf("arpa") === 0) {
      cleanupCoundownARPA = cleanupInterval;
      setArpaObject(data.data);
    }

    if (data.message_id.indexOf("cbf") === 0) {
      cleanupCoundownCBF = cleanupInterval;
      setCBFObject(data.data.cbf);
      const d = new Date();
      let time = d.getTime();
      countdown = Number(data.data.maneuver_start) - time / 1000;
    }
  }, [data, setMapCenter, setGunnerusHeading]);

  useEffect(() => {
    const interval = setInterval(() => {
      setAisData(() => {
        return Object.values(aisObject);
      });

      countdown -= refreshInterval / 1000;
      if (countdown < 0) countdown = -1;
      cleanupCoundownARPA -= refreshInterval;
      if (cleanupCoundownARPA < 0) setArpaObject([]);
      cleanupCoundownCBF -= refreshInterval;
      if (cleanupCoundownCBF < 0) setCBFObject([]);
      setCbftimer(countdown.toFixed(2));
    }, refreshInterval);
    return () => {
      clearInterval(interval);
    };
  }, []);

  const listTooltips = getTooltips(
    aisData,
    aisObject,
    arpaObject,
    settings,
    gunnerusHeading
  );

  const listVessels = aisData.map((ais) => {
    if (
      isNaN(Number(ais.lat)) ||
      isNaN(Number(ais.lon)) ||
      ais.speed === 0 ||
      !ais.hasOwnProperty("heading") ||
      !ais.hasOwnProperty("speed")
    )
      return null;

    function rotate_heaidng(ais_in) {
      if (ais_in.heading) {
        return ais_in.heading;
      } else {
        return 0;
      }
    }

    return (
      <Overlay
        key={"1" + String(ais.mmsi)}
        anchor={[Number(ais.lat), Number(ais.lon)]}
        offset={[16, 44]}
      >
        <img
          className="overlay"
          src={boat}
          style={{
            transform: `scale(${zoomScale}) rotate(${rotate_heaidng(ais)}deg) `,
          }}
        />
      </Overlay>
    );
  });

  const listCourses = getCourses(aisData, getGeoLine);
  const listMarkers = getMarkers(aisData, aisObject, setTipText, markerSize);
  const listArpa = getArpa(
    settings,
    arpaObject,
    getGeoCircle,
    getGeoLine,
    anchor,
    zoomScale
  );
  const listPreviousPaths = getPaths(aisData, getGeoLine);

  const draggable = settings.showDebugOverlay ? (
    <Draggable offset={[900, 450]} anchor={anchor} onDragEnd={setAnchor}>
      <p className="block">{tipText}</p>
    </Draggable>
  ) : null;

  const controls = settings.showSimControls ? (
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

  const maneuverCountdown =
    countdown > 0 ? (
      <Overlay key={"coundownoverlay"} anchor={mapCenter} offset={[100, -100]}>
        <TableContainer
          component={Paper}
          key={"maneuvercountdowntable"}
          style={{
            transform: `rotate(${
              settings.navigationMode ? gunnerusHeading : 0
            }deg) `,

            opacity: 0.85,
          }}
        >
          <Table sx={{ maxWidth: 250 }} size="small" aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell align="right">t. remain.</TableCell>
                <TableCell align="left">unit</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow
                key={"maneuverCountdownrow"}
                sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
              >
                <TableCell align="right">{cbfTimer}</TableCell>
                <TableCell align="left">s</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Overlay>
    ) : null;

  return (
    <div className="mapcontainer">
      <div
        className="map"
        style={{
          transform: `rotate(${
            settings.navigationMode ? -gunnerusHeading : 0
          }deg) `,
        }}
      >
        <Map
          defaultCenter={mapCenter}
          defaultZoom={15}
          center={mapCenter}
          onBoundsChanged={handleZoomLevel}
        >
          {listPreviousPaths}
          <GeoJson
            key={"180"}
            data={getGeoLine(cbfObject)}
            styleCallback={(feature, hover) => {
              return {
                fill: "#00000000",
                strokeWidth: "4",
                opacity: 0.8,
                stroke: "red",
                r: "20",
              };
            }}
          />
          {listArpa}
          {listCourses}
          {listVessels}
          {listTooltips}
          {listMarkers}
          <Overlay anchor={mapCenter} offset={[16, 44]}>
            <img
              className="overlay"
              src={gunnerus}
              style={{
                transform: `rotate(${gunnerusHeading}deg) scale(${zoomScale})`,
              }}
            />
          </Overlay>
          {maneuverCountdown}
          <Marker
            key={0}
            color="red"
            width={markerSize}
            anchor={mapCenter}
          ></Marker>
          {draggable}
        </Map>
      </div>
      {controls}
    </div>
  );
};

export default MyMap;
