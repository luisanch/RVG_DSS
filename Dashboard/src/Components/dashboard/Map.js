import React, { Fragment, useEffect, useState } from "react";
import { Map, Marker, Overlay, GeoJson, Draggable } from "pigeon-maps";
import "./Map.css";
import gunnerus from "../../Assets/ships/gunnerus.svg";
import boat from "../../Assets/ships/boat.svg";
import boat_s from "../../Assets/ships/boat_s.svg";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Stack from "@mui/material/Stack";
import Slider from "@mui/material/Slider";
import Paper from "@mui/material/Paper";
import { maxHeight } from "@mui/system";

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
  const arpaColor = "black";
  const courseColor = "orange";
  const previousPathColor = "blue";

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
    console.log(message);
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

  var createGeoJSONCircle = function (center, radiusInKm, points) {
    if (!points) points = 64;

    var coords = {
      latitude: center[1],
      longitude: center[0],
    };

    var km = radiusInKm;

    var ret = [];
    var distanceX = km / (111.32 * Math.cos((coords.latitude * Math.PI) / 180));
    var distanceY = km / 110.574;

    var theta, x, y;
    for (var i = 0; i < points; i++) {
      theta = (i / points) * (2 * Math.PI);
      x = distanceX * Math.cos(theta);
      y = distanceY * Math.sin(theta);

      ret.push([coords.longitude + x, coords.latitude + y]);
    }
    ret.push(ret[0]);

    return [ret];
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

  const getGeoPoint = (coord) => {
    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: { type: "Point", coordinates: coord },
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
      // console.log(data);

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
      // console.log(JSON.stringify(data.data.maneuver_start, null, 2));
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

      // console.log(countdown);
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

  const listTooltips = aisData.map((ais) => {
    if (isNaN(Number(ais.lat)) || isNaN(Number(ais.lon))) return null;

    if (!aisObject[ais.mmsi].hasOwnProperty("pinTooltip")) {
      aisObject[ais.mmsi]["pinTooltip"] = false;
      aisObject[ais.mmsi]["hoverTooltip"] = false;
    }
    const hasArpa = arpaObject.hasOwnProperty(ais.mmsi);

    const formatString = (text, maxLength = 9) => {
      const stringText = String(text);
      if (stringText.length > maxLength) {
        return stringText.slice(0, maxLength);
      } else {
        return stringText;
      }
    };

    const tooltipText = (ais) => {
      const hasSafetyParams = hasArpa && arpaObject[ais.mmsi].safety_params;

      const lon = ais.lon;
      const lat = ais.lat;
      const course = ais.hasOwnProperty("course")
        ? ais.course.toFixed(2)
        : "--";
      const mmsi = ais.mmsi;
      const speed = ais.hasOwnProperty("speed") ? ais.speed.toFixed(2) : "--";
      const d2cpa = hasArpa
        ? Number(arpaObject[ais.mmsi]["d_2_cpa"]).toFixed(2)
        : "--";
      const t2cpa = hasArpa
        ? Number(arpaObject[ais.mmsi]["t_2_cpa"]).toFixed(2)
        : "--";
      const dAtcpa = hasArpa
        ? Number(arpaObject[ais.mmsi]["d_at_cpa"]).toFixed(2)
        : "--";
      const t2r = hasSafetyParams
        ? Number(arpaObject[ais.mmsi]["t_2_r"]).toFixed(2)
        : "--";
      const d2r = hasSafetyParams
        ? Number(arpaObject[ais.mmsi]["d_2_r"]).toFixed(2)
        : "--";

      function createData(parameter, value, unit) {
        return { parameter, value, unit };
      }

      const rows = settings.shortTooltips
        ? [
            createData("T2CPA", formatString(t2cpa), "s"),
            createData("D2CPA", formatString(d2cpa), "m"),
            createData("D@CPA", formatString(dAtcpa), "m"),
            createData("T2R", formatString(t2r), "s"),
            createData("D2R", formatString(d2r), "m"),
          ]
        : [
            createData("MMSI", mmsi, "#"),
            createData("Longitude", lon, "DD"),
            createData("Latitude", lat, "DD"),
            createData("Course", course, "°"),
            createData("Speed", speed, "kn"),
            createData("T. to CPA", formatString(t2cpa), "s"),
            createData("Dist. to CPA", formatString(d2cpa), "m"),
            createData("Dist. at CPA", formatString(dAtcpa), "m"),
            createData("T. to Saf. R", formatString(t2r), "s"),
            createData("Dist. to Saf. R", formatString(d2r), "m"),
          ];

      return (
        <TableContainer
          component={Paper}
          style={{
            transform: `scale(${0.77})  rotate(${
              settings.navigationMode ? gunnerusHeading : 0
            }deg) `,
            opacity: 0.85,
          }}
        >
          <Table sx={{ maxWidth: 285 }} size="small" aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell align="left">
                  {settings.shortTooltips ? "Par." : "Parameter"}
                </TableCell>
                <TableCell align="right">
                  {settings.shortTooltips ? "Val." : "Value"}
                </TableCell>
                <TableCell align="right">
                  {settings.shortTooltips ? "U." : "Units"}
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow
                  key={row.parameter}
                  sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                >
                  <TableCell align="left">{row.parameter}</TableCell>
                  <TableCell align="right">{row.value}</TableCell>
                  <TableCell align="right">{row.unit}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      );
    };

    const tooltipOverlay = (
      <Overlay
        key={"6" + ais.mmsi}
        anchor={[ais.lat, ais.lon]}
        offset={settings.shortTooltips ? [25, 190] : [30, 340]}
      >
        {tooltipText(ais)}
      </Overlay>
    );

    const tooltip =
      aisObject[ais.mmsi]["hoverTooltip"] ||
      aisObject[ais.mmsi].pinTooltip ||
      (settings.showAllTooltips && hasArpa)
        ? tooltipOverlay
        : null;

    return tooltip;
  });

  const listMarkers = aisData.map((ais) => {
    if (isNaN(Number(ais.lat)) || isNaN(Number(ais.lon))) return null;

    return (
      <Marker
        key={ais.mmsi}
        color="green"
        width={markerSize}
        onClick={() => {
          setTipText(JSON.stringify(ais, null, 2));
          aisObject[ais.mmsi].pinTooltip = !aisObject[ais.mmsi].pinTooltip;
        }}
        onMouseOver={() => {
          aisObject[ais.mmsi]["hoverTooltip"] = true;
        }}
        onMouseOut={() => (aisObject[ais.mmsi]["hoverTooltip"] = false)}
        anchor={[Number(ais.lat), Number(ais.lon)]}
      />
    );
  });

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

  const listCourses = aisData.map((ais) => {
    if (
      isNaN(Number(ais.lat)) ||
      isNaN(Number(ais.lon)) ||
      !ais.hasOwnProperty("lat_p") ||
      !ais.hasOwnProperty("lon_p") ||
      ais.speed <= 0
    )
      return null;

    return (
      <GeoJson
        key={"2" + String(ais.mmsi)}
        data={getGeoLine([
          [ais.lon, ais.lat],
          [ais.lon_p, ais.lat_p],
        ])}
        styleCallback={(feature, hover) => {
          return {
            fill: "#00000000",
            strokeWidth: "2",
            stroke: courseColor,
            r: "20",
          };
        }}
      />
    );
  });

  const listPreviousPaths = aisData.map((ais) => {
    if (isNaN(Number(ais.lat)) || isNaN(Number(ais.lon)) || ais.speed <= 0)
      return null;

    return (
      <GeoJson
        key={"2" + String(ais.mmsi)}
        data={getGeoLine(ais.pos_history)}
        styleCallback={(feature, hover) => {
          return {
            fill: "#00000000",
            strokeWidth: "1",
            opacity: 0.5,
            stroke: previousPathColor,
            r: "20",
          };
        }}
      />
    );
  });

  const listArpa = Object.values(arpaObject).map((arpa, index) => {
    if (!settings.showHitbox) return null;

    let cpa = (
      <GeoJson
        key={"0" + index}
        data={getGeoLine([
          [anchor[1], anchor[0]],
          [arpa.lon_at_cpa, arpa.lat_at_cpa],
          [arpa.lon_o_at_cpa, arpa.lat_o_at_cpa],
          [arpa.lon_o, arpa.lat_o],
        ])}
        styleCallback={(feature, hover) => {
          return {
            fill: "#00000000",
            strokeWidth: "2",
            opacity: 0.2,
            stroke: arpaColor,
            r: "20",
          };
        }}
      />
    );

    let cpa_target_vessel = (
      <Overlay
        key={"4" + index}
        anchor={[arpa.lat_o_at_cpa, arpa.lon_o_at_cpa]}
        offset={[16, 44]}
      >
        <img
          className="overlay"
          src={boat}
          style={{
            transform: `scale(${zoomScale}) rotate(${arpa.course}deg) `,
            opacity: 0.5,
          }}
        />
      </Overlay>
    );

    const cpa_self_vessel = (
      <Overlay
        key={"5" + index}
        anchor={[arpa.lat_at_cpa, arpa.lon_at_cpa]}
        offset={[16, 44]}
      >
        <img
          className="overlay"
          src={gunnerus}
          style={{
            transform: `scale(${zoomScale}) rotate(${arpa.self_course}deg) `,
            opacity: 0.5,
          }}
        />
      </Overlay>
    );

    if (arpa.safety_params) {
      const geoCircle = createGeoJSONCircle(
        [arpa.lon_o_at_r, arpa.lat_o_at_r],
        arpa.safety_radius / 1000
      );

      let safety_r = (
        <GeoJson
          key={"1" + index}
          data={getGeoCircle(geoCircle)}
          styleCallback={(feature, hover) => {
            return {
              fill: "#00000000",
              strokeWidth: "2",
              opacity: 0.2,
              stroke: arpaColor,
              r: "20",
            };
          }}
        />
      );

      const safety_self_vessel = (
        <Overlay
          key={"6" + index}
          anchor={[arpa.lat_at_r, arpa.lon_at_r]}
          offset={[16, 44]}
        >
          <img
            className="overlay"
            src={boat_s}
            style={{
              transform: `scale(${zoomScale}) rotate(${arpa.self_course}deg) `,
              opacity: 0.5,
            }}
          />
        </Overlay>
      );

      return [
        cpa,
        cpa_target_vessel,
        cpa_self_vessel,
        safety_self_vessel,
        safety_r,
      ];
    }

    return [cpa, cpa_target_vessel, cpa_self_vessel];
  });

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
