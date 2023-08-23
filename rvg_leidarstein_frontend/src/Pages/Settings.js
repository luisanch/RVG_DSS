/**
 * A React component representing the settings form.
 * It allows users to configure various settings for the application.
 * The settings include ARPA data display, tooltips, navigation mode, simulation controls, and data mode.
 *
 * @param {object} props - The props object that contains the following properties:
 *   @param {object} settings - An object representing the current settings for the application.
 *   @param {function} setSettings - A function to update the settings state in the parent component.
 *   @param {function} sendMessage - A function to send messages to the server (for simulation control).
 *
 * @returns {JSX.Element} - Returns a JSX element containing the settings form.
 */
import React, { useState } from "react";
import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
} from "@mui/material";
import DomainCanvas from "./SettingsUtils/DomainCanvas";

export default function Settings(props) {
  // Extracting props
  const setAppSettings = props.setSettings;
  const [settings, setSettings] = useState(props.settings);
  const sendMessage = props.sendMessage;

  // Event handlers for setting changes
  const handleChangeHitbox = (event) => {
    update("showHitbox", event.target.checked);
  };

  const handleChangeNavigation = (event) => {
    update("navigationMode", event.target.checked);
  };

  const handleChangeShortTooltips = (event) => {
    update("shortTooltips", event.target.checked);
  };

  const handleChangeTooltips = (event) => {
    update("showAllTooltips", event.target.checked);
  };

  const handleShowSimControls = (event) => {
    update("showSimControls", event.target.checked);
  };

  const handleShowDomains = (event) => {
    update("showDomains", event.target.checked);
  };

  const handleSimMode = (event) => {
    update("simMode", event.target.value);
    const message = {
      type: "datain",
      content: {
        message_id: "data_mode",
        val: event.target.value,
      },
    };
    sendMessage(JSON.stringify(message, null, 2));
  };

  // Function to update settings and propagate changes to parent component
  const update = (setting, value) => {
    let newSettings = props.settings;
    newSettings[setting] = value;
    setSettings(newSettings);
    setAppSettings(newSettings);
  };

  return (
    <div className="ControlsRow">
      <FormGroup>
        {/* Checkboxes for various settings */}
        <FormControlLabel
          control={
            <Checkbox
              id="hitbox"
              checked={settings.showHitbox}
              onChange={handleChangeHitbox}
            />
          }
          label="Show ARPA data"
        />
        <FormControlLabel
          control={
            <Checkbox
              id="compacttooltips"
              disabled={!settings.showHitbox}
              checked={settings.shortTooltips}
              onChange={handleChangeShortTooltips}
            />
          }
          label="Compact ARPA tooltips"
        />
        <FormControlLabel
          control={
            <Checkbox
              id="alwaysdisptootltips"
              disabled={!settings.showHitbox}
              checked={settings.showAllTooltips}
              onChange={handleChangeTooltips}
            />
          }
          label="Always display ARPA tooltips"
        />
        <FormControlLabel
          control={
            <Checkbox
              id="navmodeon"
              checked={settings.navigationMode}
              onChange={handleChangeNavigation}
            />
          }
          label="Navigation Mode On"
        />
        <FormControlLabel
          control={
            <Checkbox
              id="showsimcontrols"
              checked={settings.showSimControls}
              onChange={handleShowSimControls}
            />
          }
          label="Show Sim. Controls"
        />
        <FormControlLabel
          control={
            <Checkbox
              id="showdomains"
              checked={settings.showDomains}
              onChange={handleShowDomains}
            />
          }
          label="Show CBF Domains"
        />
        {/* Select menu for data mode */}
        <FormControl sx={{ m: 1, minWidth: 120 }} size="small">
          <Select
            labelId="simMode-label"
            value={settings.simMode}
            onChange={handleSimMode}
          >
            <MenuItem value={"4dof"}>4 DOF Sim.</MenuItem>
            <MenuItem value={"rt"}>Real Time</MenuItem>
          </Select>
          <FormHelperText>Data Mode</FormHelperText>
        </FormControl>
      </FormGroup>
      <DomainCanvas sendMessage={sendMessage} />
    </div>
  );
}
