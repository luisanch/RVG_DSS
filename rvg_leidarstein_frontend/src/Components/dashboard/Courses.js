import { GeoJson } from "pigeon-maps";

const courseColor = "orange";

function getCourses(aisData, getGeoLine) {
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

  return listCourses;
}

export default getCourses;
