/**
 * Convert a coordinate in degrees/minutes format to decimal degrees.
 * @param {number} coord - The coordinate value in degrees/minutes format (e.g., 5545.1234).
 * @param {string} direction - The direction of the coordinate ('N', 'S', 'E', or 'W').
 * @returns {number} - The converted coordinate value in decimal degrees.
 */
export function deg2dec(coord, direction) {
  let dir = 1;
  if (direction === "S" || direction === "W") dir = -1;
  let deg = Math.trunc(coord / 100);
  let dec = (coord / 100 - deg) * (10 / 6);
  return dir * (deg + dec);
}

/**
 * Generate a GeoJSON LineString feature from an array of points.
 * @param {Array} points - Array of [longitude, latitude] points to form the line.
 * @returns {Object} - GeoJSON LineString feature.
 */
export function getGeoLine(points) {
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
}

/**
 * Generate a GeoJSON Polygon feature from a circular path represented as a GeoJSON object.
 * @param {Object} geoCircle - The GeoJSON object representing the circular path.
 * @returns {Object} - GeoJSON Polygon feature.
 */
export function getGeoCircle(geoCircle) {
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
}
