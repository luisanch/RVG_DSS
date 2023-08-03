import React, { useEffect, useState } from "react";
import { Map, Marker, Overlay, GeoJson, Draggable } from "pigeon-maps";
import getMarkers from "./Markers";
import getArpa from "./Arpa";
import getPaths from "./Paths";
import getCourses from "./Courses";
import getTooltips from "./Tooltips";
import getVessels from "./Vessels";
import Controls from "./Controls";
import getManeuverCountdown from "./ManeuverCountdown";
import "./Map.css";
import gunnerus from "../../Assets/ships/gunnerus.svg";
import { deg2dec, getGeoCircle, getGeoLine } from "../utils";

// Define a blank object to store AIS data and other variables
const aisObject = {};
let countdown = -1;
const refreshInterval = 500;
const cleanupInterval = 15000;
let cleanupCountdownARPA = cleanupInterval;
let cleanupCoundownCBF = cleanupInterval;

// Main map component
const MyMap = (props) => {
  // Destructure the props
  const data = props.data;
  const sendMessage = props.sendMessage;
  const markerSize = 20;
  const settings = props.settings;

  // State variables to manage the map's center, heading, AIS data, etc.
  const [mapCenter, setMapCenter] = useState([63.43463, 10.39744]);
  const [gunnerusHeading, setGunnerusHeading] = useState(0);
  const [aisData, setAisData] = useState([]);
  const [anchor, setAnchor] = useState([63.43463, 10.39744]);
  const [tipText, setTipText] = useState("");
  const [arpaObject, setArpaObject] = useState([]);
  const [cbfObject, setCBFObject] = useState([]);
  const [zoomScale, setZoomScale] = useState(1);
  const [cbfTimer, setCbftimer] = useState();

  // Function to handle zoom level changes
  const handleZoomLevel = (event) => {
    const scale = event.zoom / (2 * 18);
    setZoomScale(scale);
  };

  // Function to set the position of the ship "Gunnerus"
  function setGunnerusPos(data) {
    const lon = data.lon;
    const lon_dir = data.lon_dir;
    const lat = data.lat;
    const lat_dir = data.lat_dir;
    const res = [deg2dec(lat, lat_dir), deg2dec(lon, lon_dir)];
    setMapCenter(res);
    setAnchor(res);
  }

  // Function to update AIS data for a specific MMSI
  function setAisObjectData(data) {
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

  // Function to clear colav data after a certain interval
  function clearColavData() {
    countdown -= refreshInterval / 1000;
    if (countdown < 0) countdown = -1;
    cleanupCountdownARPA -= refreshInterval;
    if (cleanupCountdownARPA < 0) setArpaObject([]);
    cleanupCoundownCBF -= refreshInterval;
    if (cleanupCoundownCBF < 0) setCBFObject([]);
    setCbftimer(countdown.toFixed(2));
  }

  // Effect hook to handle incoming data and update state variables accordingly
  useEffect(() => {
    if (!data) return;
    if (data.message_id === "$GPGGA_ext") {
      setGunnerusPos(data);
    }

    if (data.message_id === "$PSIMSNS_ext") {
      setGunnerusHeading(data.head_deg);
    }

    if (data.message_id.indexOf("!AI") === 0) {
      setAisObjectData(data);
    }

    if (data.message_id.indexOf("arpa") === 0) {
      cleanupCountdownARPA = cleanupInterval;
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

  // Effect hook to update AIS data and perform cleanup at regular intervals
  useEffect(() => {
    const interval = setInterval(() => {
      setAisData(() => {
        return Object.values(aisObject);
      });

      clearColavData();
    }, refreshInterval);
    return () => {
      clearInterval(interval);
    };
  }, []);

  // Generate tooltips based on AIS data, ARPA data, and settings
  const listTooltips = getTooltips(
    aisData,
    aisObject,
    arpaObject,
    settings,
    gunnerusHeading
  );

  // Generate vessel markers based on AIS data and zoom scale
  const listVessels = getVessels(aisData, zoomScale);

  // Generate courses based on AIS data
  const listCourses = getCourses(aisData);

  // Generate marker elements based on AIS data, anchor, tooltip text, and marker size
  const listMarkers = getMarkers(aisData, aisObject, setTipText, markerSize);

  // Generate ARPA objects based on settings, ARPA data, anchor, and zoom scale
  const listArpa = getArpa(settings, arpaObject, anchor, zoomScale);

  // Generate previous paths based on AIS data
  const listPreviousPaths = getPaths(aisData);

  // Generate countdown element for maneuver countdown
  const maneuverCountdown = getManeuverCountdown(
    mapCenter,
    settings,
    gunnerusHeading,
    countdown,
    cbfTimer
  );

  return (
    <div className="mapcontainer">
      <div
        className="map"
        //  Handle the rotation for the map
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

          {/* Draw CBF based suggestion for trajectory */}
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

          {/* Draw Gunnerus ship asset*/}
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

          {/* Draw Gunnerus marker*/}
          <Marker
            key={0}
            color="red"
            width={markerSize}
            anchor={mapCenter}
          ></Marker>
        </Map>
      </div>

      {/* Render the controls component and pass settings and sendMessage as props */}
      <Controls settings={settings} sendMessage={sendMessage} />
    </div>
  );
};

export default MyMap;
