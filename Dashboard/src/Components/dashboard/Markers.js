import React from "react";
import { Map, Marker } from "pigeon-maps";
import "./Map.css";

const Markers = () => { 

  const coords = [[63.43466, 10.39748],
    [63.43465, 10.39742]]
  
    const listMarkers = coords.map(coord =>
      <Marker width={50} anchor={coord}/>
    );
  return  <Map>{listMarkers}</Map>;
};

export default Markers;
