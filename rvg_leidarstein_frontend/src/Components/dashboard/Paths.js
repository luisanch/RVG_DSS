import { GeoJson } from "pigeon-maps";
import { getGeoLine } from "../utils";

const previousPathColor = "blue";

// Function to generate travel paths based on AIS data
function getPaths(aisData) {
  // Create an array of travel paths based on AIS data
  const listPreviousPaths = aisData.map((ais) => {
    // Check if the latitude or longitude is not a number (invalid data) or the speed is zero or negative
    if (isNaN(Number(ais.lat)) || isNaN(Number(ais.lon)) || ais.speed <= 0)
      return null;

    // Return a GeoJson component representing the previous path
    return (
      <GeoJson
        key={"2" + String(ais.mmsi)} // Unique key for the GeoJson component (uses AIS MMSI as the key)
        data={getGeoLine(ais.pos_history)} // Get the GeoJSON LineString data from AIS position history
        styleCallback={(feature, hover) => {
          // Style callback function to customize the appearance of the path
          return {
            fill: "#00000000", // Transparent fill
            strokeWidth: "1", // Width of the stroke (path line)
            opacity: 0.5, // Opacity of the path
            stroke: previousPathColor, // Color of the path
            r: "20", // Radius of the path (not applicable for a line)
          };
        }}
      />
    );
  });

  // Return the array of previous paths
  return listPreviousPaths;
}

// Export the getPaths function to make it accessible from other modules
export default getPaths;
