import boat from "../../Assets/ships/boat.svg";
import { Overlay } from "pigeon-maps";

/**
 * Function to generate vessel icons (boats) for AIS data on the map.
 * @param {Array} aisData - Array of AIS data objects.
 * @param {number} zoomScale - Zoom scale factor for the vessel icons.
 * @returns {Array} - Array of Overlay elements containing vessel icons to be displayed on the map.
 */
function getVessels(aisData, zoomScale) {
  // Create an array of vessel icons for each AIS data entry
  const listVessels = aisData.map((ais) => {
    // Check if the latitude, longitude, speed, heading properties are valid, and if not, return null (no vessel icon)
    if (
      isNaN(Number(ais.lat)) ||
      isNaN(Number(ais.lon)) ||
      ais.speed === 0 ||
      !ais.hasOwnProperty("heading") ||
      !ais.hasOwnProperty("speed")
    )
      return null;

    // Function to determine the heading (rotation) of the vessel icon
    function rotate_heading(ais_in) {
      if (ais_in.heading) {
        return ais_in.heading;
      } else {
        return 0;
      }
    }

    // Return an Overlay with the vessel icon (boat) positioned based on the AIS location and heading
    return (
      <Overlay
        key={"1" + String(ais.mmsi)}
        anchor={[Number(ais.lat), Number(ais.lon)]}
        offset={[16, 44]}
      >
        <img
          className="overlay"
          src={boat}
          style={{
            transform: `scale(${zoomScale}) rotate(${rotate_heading(ais)}deg) `,
          }}
        />
      </Overlay>
    );
  });

  // Return the array of vessel icons
  return listVessels;
}

// Export the getVessels function to make it accessible from other modules
export default getVessels;
