import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { Overlay } from "pigeon-maps";

// Function to generate the maneuver countdown item
function getManeuverCountdown(
  mapCenter, // Current center coordinates of the map
  settings, // Settings object that controls map behavior
  gunnerusHeading, // Current heading angle of the main vessel (Gunnerus)
  countdown, // Remaining time in seconds for the maneuver countdown
  cbfTimer // Countdown timer for the specific maneuver
) {
  // Generate the maneuver countdown table overlay if there's an active maneuver countdown
  const maneuverCountdown =
    countdown > 0 ? ( // If there's an active countdown
      <Overlay key={"coundownoverlay"} anchor={mapCenter} offset={[100, -100]}>
        <TableContainer
          component={Paper}
          key={"maneuvercountdowntable"}
          style={{
            transform: `rotate(${
              settings.navigationMode ? gunnerusHeading : 0
            }deg) `,
            opacity: 0.85, // Opacity of the countdown table overlay
          }}
        >
          <Table sx={{ maxWidth: 250 }} size="small" aria-label="a dense table">
            <TableHead>
              <TableRow>
                {/* Countdown time */}
                <TableCell align="right">t. remain.</TableCell>
                {/* Time unit (seconds) */}
                <TableCell align="left">unit</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow
                key={"maneuverCountdownrow"} // Unique key for the table row
                sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
              >
                {/* Display the countdown timer */}
                <TableCell align="right">{cbfTimer}</TableCell>
                {/* Time unit label (seconds) */}
                <TableCell align="left">s</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Overlay>
    ) : null; // If there's no active countdown, return null (no overlay)

  // Return the maneuver countdown overlay (if active) or null (if not active)
  return maneuverCountdown;
}

// Export the getManeuverCountdown function to make it accessible from other modules
export default getManeuverCountdown;
