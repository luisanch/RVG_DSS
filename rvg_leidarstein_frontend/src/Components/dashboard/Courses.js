import { GeoJson } from "pigeon-maps";
import { getGeoLine } from "../utils";

// Course color used for rendering course lines on the map
const courseColor = "orange";

// Function to generate GeoJson components for rendering course lines
function getCourses(aisData) {
  // Map through the aisData array to create a list of GeoJson components
  const listCourses = aisData.map((ais) => {
    // Check if AIS data is valid for rendering course line
    if (
      ais.lat_p == null ||
      ais.lon_p == null  
    ) {
      // If data is not valid, return null (no course line to render)
      return null;
    }

    // If AIS data is valid, create a GeoJson component representing the course line
    return (
      <GeoJson
        key={"2" + String(ais.mmsi)}
        data={getGeoLine([
          [ais.lon, ais.lat], // Starting point coordinates (current position)
          [ais.lon_p, ais.lat_p], // Ending point coordinates (previous position)
        ])}
        styleCallback={(feature, hover) => {
          // Style the course line
          return {
            fill: "#00000000", // Transparent fill
            strokeWidth: "2", // Stroke width
            stroke: courseColor, // Stroke color
            r: "20", // Radius (used for GeoJson circles)
          };
        }}
      />
    );
  });

  // Return the list of course lines (GeoJson components)
  return listCourses;
}

// Export the getCourses function to make it accessible from other modules
export default getCourses;
