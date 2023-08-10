import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";

import { Overlay } from "pigeon-maps";

// Function to generate tooltips for AIS data on the map
function getTooltips(
  aisData,
  aisObject,
  arpaObject,
  encounterData,
  settings,
  gunnerusHeading
) {
  // Create an array of tooltips for each AIS data entry
  const listTooltips = aisData.map((ais) => {
    // Check if the latitude or longitude is not a number (invalid data), and if so, return null (no tooltip)
    if (isNaN(Number(ais.lat)) || isNaN(Number(ais.lon))) return null;

    // If the AIS object does not have the 'pinTooltip' and 'hoverTooltip' properties, set them to false
    if (!aisObject[ais.mmsi].hasOwnProperty("pinTooltip")) {
      aisObject[ais.mmsi]["pinTooltip"] = false;
      aisObject[ais.mmsi]["hoverTooltip"] = false;
    }

    // Check if ARPA data exists for this AIS entry
    const hasArpa = arpaObject.hasOwnProperty(ais.mmsi);

    // Function to format text strings with a maximum length
    const formatString = (text, maxLength = 9) => {
      const stringText = String(text);
      if (stringText.length > maxLength) {
        return stringText.slice(0, maxLength);
      } else {
        return stringText;
      }
    };

    // Function to create tooltip content based on AIS and ARPA data
    const tooltipText = (ais) => {
      // Check if AIS data includes ARPA parameters
      const hasSafetyParams = hasArpa && arpaObject[ais.mmsi].safety_params;

      // Extract necessary information from AIS and ARPA data
      const lon = ais.lon;
      const lat = ais.lat;
      const course = ais.hasOwnProperty("course")
        ? ais.course.toFixed(2)
        : "--";
      const mmsi = ais.mmsi;
      const speed = ais.hasOwnProperty("speed") ? ais.speed.toFixed(2) : "--";
      const d2cpa = hasArpa
        ? Number(arpaObject[ais.mmsi]["d_2_cpa"]).toFixed(2)
        : "--";
      const t2cpa = hasArpa
        ? Number(arpaObject[ais.mmsi]["t_2_cpa"]).toFixed(2)
        : "--";
      const dAtcpa = hasArpa
        ? Number(arpaObject[ais.mmsi]["d_at_cpa"]).toFixed(2)
        : "--";
      const t2r = hasSafetyParams
        ? Number(arpaObject[ais.mmsi]["t_2_r"]).toFixed(2)
        : "--";
      const d2r = hasSafetyParams
        ? Number(arpaObject[ais.mmsi]["d_2_r"]).toFixed(2)
        : "--";

      let encounter = "--";

      if (encounterData.hasOwnProperty(ais.mmsi)) {
        switch (encounterData[ais.mmsi]) {
          case 1:
            encounter = "Safe";
            break;
          case 2:
            encounter = "Otk. Star";
            break;
          case 3:
            encounter = "Otk. Port";
            break;
          case 4:
            encounter = "Head On";
            break;
          case 5:
            encounter = "Give Way";
            break;
          case 6:
            encounter = "Stand On";
            break;
          default:
            encounter = "--";
        }
      }

      // Function to create data objects for the tooltip table
      function createData(parameter, value, unit) {
        return { parameter, value, unit };
      }

      // Define rows for the tooltip table based on settings
      const rows = settings.shortTooltips
        ? [
            createData("Ectr.", encounter, "t"),
            createData("T2CPA", formatString(t2cpa), "s"),
            createData("D2CPA", formatString(d2cpa), "m"),
            createData("D@CPA", formatString(dAtcpa), "m"),
            createData("T2R", formatString(t2r), "s"),
            createData("D2R", formatString(d2r), "m"),
          ]
        : [
            createData("MMSI", mmsi, "#"),
            createData("Encounter", encounter, "t"),
            createData("Longitude", lon, "DD"),
            createData("Latitude", lat, "DD"),
            createData("Course", course, "°"),
            createData("Speed", speed, "kn"),
            createData("T. to CPA", formatString(t2cpa), "s"),
            createData("Dist. to CPA", formatString(d2cpa), "m"),
            createData("Dist. at CPA", formatString(dAtcpa), "m"),
            createData("T. to Saf. R", formatString(t2r), "s"),
            createData("Dist. to Saf. R", formatString(d2r), "m"),
          ];

      // Return a Paper-wrapped TableContainer with the tooltip table
      return (
        <TableContainer
          component={Paper}
          style={{
            transform: `scale(${0.77})  rotate(${
              settings.navigationMode ? gunnerusHeading : 0
            }deg) `,
            opacity: 0.85,
          }}
        >
          <Table sx={{ maxWidth: 285 }} size="small" aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell align="left">
                  {settings.shortTooltips ? "Par." : "Parameter"}
                </TableCell>
                <TableCell align="right">
                  {settings.shortTooltips ? "Val." : "Value"}
                </TableCell>
                <TableCell align="right">
                  {settings.shortTooltips ? "U." : "Units"}
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow
                  key={row.parameter}
                  sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                >
                  <TableCell align="left">{row.parameter}</TableCell>
                  <TableCell align="right">{row.value}</TableCell>
                  <TableCell align="right">{row.unit}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      );
    };

    // Create an overlay with the tooltip content positioned based on the AIS location
    const tooltipOverlay = (
      <Overlay
        key={"6" + ais.mmsi}
        anchor={[ais.lat, ais.lon]}
        offset={settings.shortTooltips ? [25, 190] : [30, 340]}
      >
        {tooltipText(ais)}
      </Overlay>
    );

    // Determine whether to show the tooltip based on settings and hover/pin states
    const tooltip =
      aisObject[ais.mmsi]["hoverTooltip"] ||
      aisObject[ais.mmsi].pinTooltip ||
      (settings.showAllTooltips && hasArpa)
        ? tooltipOverlay
        : null;

    // Return the tooltip (or null if not shown)
    return tooltip;
  });

  // Return the array of tooltips
  return listTooltips;
}

// Export the getTooltips function to make it accessible from other modules
export default getTooltips;
