import React from "react"; 
import "./Map.css";

const InfoTip = (props) => { 

  const coords = props.coords
  
    const listMarkers = coords.map(coord =>
      <Marker width={50} anchor={coord}/>
    );
  return  <Map>{listMarkers}</Map>;
};

export default Markers;
