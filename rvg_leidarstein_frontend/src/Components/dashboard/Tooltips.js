import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";

import { Overlay } from "pigeon-maps";

function getTooltips(
  aisData,
  aisObject,
  arpaObject,
  settings,
  gunnerusHeading
) {
  const listTooltips = aisData.map((ais) => {
    if (isNaN(Number(ais.lat)) || isNaN(Number(ais.lon))) return null;

    if (!aisObject[ais.mmsi].hasOwnProperty("pinTooltip")) {
      aisObject[ais.mmsi]["pinTooltip"] = false;
      aisObject[ais.mmsi]["hoverTooltip"] = false;
    }
    const hasArpa = arpaObject.hasOwnProperty(ais.mmsi);

    const formatString = (text, maxLength = 9) => {
      const stringText = String(text);
      if (stringText.length > maxLength) {
        return stringText.slice(0, maxLength);
      } else {
        return stringText;
      }
    };

    const tooltipText = (ais) => {
      const hasSafetyParams = hasArpa && arpaObject[ais.mmsi].safety_params;

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

      function createData(parameter, value, unit) {
        return { parameter, value, unit };
      }

      const rows = settings.shortTooltips
        ? [
            createData("T2CPA", formatString(t2cpa), "s"),
            createData("D2CPA", formatString(d2cpa), "m"),
            createData("D@CPA", formatString(dAtcpa), "m"),
            createData("T2R", formatString(t2r), "s"),
            createData("D2R", formatString(d2r), "m"),
          ]
        : [
            createData("MMSI", mmsi, "#"),
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

    const tooltipOverlay = (
      <Overlay
        key={"6" + ais.mmsi}
        anchor={[ais.lat, ais.lon]}
        offset={settings.shortTooltips ? [25, 190] : [30, 340]}
      >
        {tooltipText(ais)}
      </Overlay>
    );

    const tooltip =
      aisObject[ais.mmsi]["hoverTooltip"] ||
      aisObject[ais.mmsi].pinTooltip ||
      (settings.showAllTooltips && hasArpa)
        ? tooltipOverlay
        : null;

    return tooltip;
  });

  return listTooltips;
}

export default getTooltips;
