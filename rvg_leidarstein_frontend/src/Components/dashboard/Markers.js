import { Marker } from "pigeon-maps";

function getMarkers(aisData, aisObject, setTipText, markerSize) {
  const markers = aisData.map((ais) => {
    if (isNaN(Number(ais.lat)) || isNaN(Number(ais.lon))) return null;

    return (
      <Marker
        key={ais.mmsi}
        color="green"
        width={markerSize}
        onClick={() => {
          setTipText(JSON.stringify(ais, null, 2));
          aisObject[ais.mmsi].pinTooltip = !aisObject[ais.mmsi].pinTooltip;
        }}
        onMouseOver={() => {
          aisObject[ais.mmsi]["hoverTooltip"] = true;
        }}
        onMouseOut={() => (aisObject[ais.mmsi]["hoverTooltip"] = false)}
        anchor={[Number(ais.lat), Number(ais.lon)]}
      />
    );
  });
  return markers;
}

export default getMarkers;
