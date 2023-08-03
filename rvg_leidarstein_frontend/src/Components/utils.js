export function deg2dec(coord, direction) {
  let dir = 1;
  if (direction === "S" || direction === "W") dir = -1;
  let deg = Math.trunc(coord / 100);
  let dec = (coord / 100 - deg) * (10 / 6);
  return dir * (deg + dec);
}

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

