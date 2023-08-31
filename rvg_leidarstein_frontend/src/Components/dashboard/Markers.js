import { Marker } from "pigeon-maps";

// Function to generate map markers for AIS data
function getMarkers(aisData, aisObject, setTipText, markerSize) {
  // Create an array of markers based on AIS data
  const markers = aisData.map((ais) => {
    

    // Return a Marker component for valid AIS data
    return (
      <Marker
        key={ais.mmsi} // Unique key for the marker (uses AIS MMSI as the key)
        color="green" // Color of the marker
        width={markerSize} // Width of the marker icon
        onClick={() => {
          // Function to handle click events on the marker
          setTipText(JSON.stringify(ais, null, 2)); // Set the tooltip text to AIS data in JSON format
          aisObject[ais.mmsi].pinTooltip = !aisObject[ais.mmsi].pinTooltip; // Toggle the pinTooltip property of the AIS object
        }}
        onMouseOver={() => {
          // Function to handle mouse over events on the marker
          aisObject[ais.mmsi]["hoverTooltip"] = true; // Set the hoverTooltip property of the AIS object to true
        }}
        onMouseOut={() => {
          // Function to handle mouse out events on the marker
          aisObject[ais.mmsi]["hoverTooltip"] = false; // Set the hoverTooltip property of the AIS object to false
        }}
        anchor={[Number(ais.lat), Number(ais.lon)]} // Set the marker anchor coordinates based on AIS data
      />
    );
  });

  // Return the array of markers
  return markers;
}

// Export the getMarkers function to make it accessible from other modules
export default getMarkers;
