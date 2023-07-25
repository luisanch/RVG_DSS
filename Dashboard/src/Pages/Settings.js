import React, { useState } from "react";
import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";
import { FormControl, InputLabel, Select, MenuItem, FormHelperText } from "@mui/material";

export default function Settings(props) {
  const setAppSettings = props.setSettings
  const [settings, setSettings] = useState(props.settings);
  const sendMessage = props.sendMessage;

  const handleChangeHitbox = (event) => {
    update("showHitbox", event.target.checked);
  };

  const handleChangeOverlay = (event) => {
    update("showDebugOverlay", event.target.checked);
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

  const update = (setting, value) => { 
    let newSettings = props.settings
    newSettings[setting] = value
    setSettings(newSettings);
    setAppSettings(newSettings); 
  };

  return (
    <FormGroup>
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
            id="showdebugoverlay"
            checked={settings.showDebugOverlay}
            onChange={handleChangeOverlay}
          />
        }
        label="Show Debug Overlay"
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
  );
}
