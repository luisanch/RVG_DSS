import { GeoJson } from "pigeon-maps";
import { getGeoLine } from "../utils";

const previousPathColor = "blue";

function getPaths(aisData) {
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

  return listPreviousPaths;
}

export default getPaths;
