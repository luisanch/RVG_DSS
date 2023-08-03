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

const aisObject = {};
let countdown = -1;
const refreshInterval = 500;
const cleanupInterval = 15000;
let cleanupCountdownARPA = cleanupInterval;
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

  const handleZoomLevel = (event) => {
    const scale = event.zoom / (2 * 18);
    setZoomScale(scale);
  };

  function setGunnerusPos(data) {
    const lon = data.lon;
    const lon_dir = data.lon_dir;
    const lat = data.lat;
    const lat_dir = data.lat_dir;
    const res = [deg2dec(lat, lat_dir), deg2dec(lon, lon_dir)];
    setMapCenter(res);
    setAnchor(res);
  }

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

  function clearColavData() {
    countdown -= refreshInterval / 1000;
    if (countdown < 0) countdown = -1;
    cleanupCountdownARPA -= refreshInterval;
    if (cleanupCountdownARPA < 0) setArpaObject([]);
    cleanupCoundownCBF -= refreshInterval;
    if (cleanupCoundownCBF < 0) setCBFObject([]);
    setCbftimer(countdown.toFixed(2));
  }

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

  const listTooltips = getTooltips(
    aisData,
    aisObject,
    arpaObject,
    settings,
    gunnerusHeading
  );

  const listVessels = getVessels(aisData, zoomScale);
  const listCourses = getCourses(aisData);
  const listMarkers = getMarkers(aisData, aisObject, setTipText, markerSize);
  const listArpa = getArpa(settings, arpaObject, anchor, zoomScale);
  const listPreviousPaths = getPaths(aisData);
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
        </Map>
      </div>
      <Controls settings={settings} sendMessage={sendMessage} />
    </div>
  );
};

export default MyMap;
