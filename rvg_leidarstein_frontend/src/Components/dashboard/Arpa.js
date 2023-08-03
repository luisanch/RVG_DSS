import { Overlay, GeoJson } from "pigeon-maps";
import { getGeoCircle, getGeoLine } from "../utils";
import boat from "../../Assets/ships/boat.svg";
import boat_s from "../../Assets/ships/boat_s.svg";
import gunnerus from "../../Assets/ships/gunnerus.svg";

/**
 * Create a GeoJSON circle feature from a center point, radius in kilometers, and number of points.
 * @param {Array} center - Array representing the center point as [longitude, latitude].
 * @param {number} radiusInKm - The radius of the circle in kilometers.
 * @param {number} [points=64] - The number of points to generate the circle (default is 64).
 * @returns {Object} - GeoJSON Polygon feature representing the circle.
 */
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

// Set the color for ARPA elements
const arpaColor = "black";

// Function to generate ARPA elements based on settings, ARPA object, anchor, and zoom scale
function getArpa(settings, arpaObject, anchor, zoomScale) {
  // Create an array of ARPA elements based on the arpaObject data
  const listArpa = Object.values(arpaObject).map((arpa, index) => {
    // Check if the ARPA parameters should be displayed based on the settings
    if (!settings.showHitbox) return null;

    // Generate a GeoJson element for the CPA line
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

    // Generate an Overlay element for the target vessel at CPA
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

    // Generate an Overlay element for the self vessel at CPA
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

    // Check if the obstacle domain should be displayed based on the settings
    if (arpa.safety_params) {
      let center = [arpa.lon_o_at_r, arpa.lat_o_at_r]
      const geoCircle = createGeoJSONCircle(
        center,
        arpa.safety_radius / 1000,
        64
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

      // Generate an Overlay element for the self vessel at safety radius
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

      // Return the ARPA elements for a vessel
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

  return listArpa;
}

export default getArpa;
