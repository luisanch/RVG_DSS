import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { Overlay } from "pigeon-maps";

function getManeuverCountdown(
  mapCenter,
  settings,
  gunnerusHeading,
  countdown,
  cbfTimer
) {
  const maneuverCountdown =
    countdown > 0 ? (
      <Overlay key={"coundownoverlay"} anchor={mapCenter} offset={[100, -100]}>
        <TableContainer
          component={Paper}
          key={"maneuvercountdowntable"}
          style={{
            transform: `rotate(${
              settings.navigationMode ? gunnerusHeading : 0
            }deg) `,

            opacity: 0.85,
          }}
        >
          <Table sx={{ maxWidth: 250 }} size="small" aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell align="right">t. remain.</TableCell>
                <TableCell align="left">unit</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow
                key={"maneuverCountdownrow"}
                sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
              >
                <TableCell align="right">{cbfTimer}</TableCell>
                <TableCell align="left">s</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Overlay>
    ) : null;

  return maneuverCountdown;
}

export default getManeuverCountdown;
