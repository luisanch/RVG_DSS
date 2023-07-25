import React from "react";
import MyMap from "../Components/dashboard/Map";

export default function Home(props) {
  const data = props.data;
  const settings = props.settings;
  const sendMessage = props.sendMessage;
  
  return <MyMap data={data} settings={settings} sendMessage={sendMessage}/>;
}
