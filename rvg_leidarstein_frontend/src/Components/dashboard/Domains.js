import { GeoJson } from "pigeon-maps";
import { getGeoLine } from "../utils";
const domainColor = "black";
// Function to generate travel paths based on AIS data
function getDomains(cbfObject, settings) {
  const show = settings.showDomains;
  if (cbfObject.length <= 0 || !show) {
    return [];
  }

  const listDomains = cbfObject.map((lineGroup) => {
    const listDomainLines = lineGroup.map((line) => {
      // console.log(JSON.stringify(line, null,2))
      // Return a GeoJson component representing the previous path
      return (
        <GeoJson
          key={line[0]} // Unique key for the GeoJson component
          data={getGeoLine(line)} // Get the GeoJSON LineString data from AIS position history
          styleCallback={(feature, hover) => {
            // Style callback function to customize the appearance of the path
            return {
              fill: "#00000000", // Transparent fill
              strokeWidth: "1", // Width of the stroke (path line)
              opacity: 0.5, // Opacity of the path
              stroke: domainColor, // Color of the path
              r: "20", // Radius of the path (not applicable for a line)
            };
          }}
        />
      );
    });
    return listDomainLines;
  });

  // Return the array of previous paths
  //   console.log(JSON.stringify(listDomains.flat(), null, 2))
  return listDomains.flat();
}

// Export the getPaths function to make it accessible from other modules
export default getDomains;
