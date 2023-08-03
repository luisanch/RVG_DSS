// Importing required dependencies and styles
import styles from "./sidenav.module.css";
import { NavLink } from "react-router-dom";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { navData } from "../lib/navData";
import { useState } from "react";

export default function Sidenav() {
  // State to track whether the side navigation is open or closed
  const [open, setOpen] = useState(true);

  // Function to toggle the state of the side navigation (open or closed)
  const toggleOpen = () => {
    setOpen(!open);
  };

  return (
    // Conditionally apply the CSS class based on the 'open' state
    <div className={open ? styles.sidenav : styles.sidenavClosed}>
      {/* Button to toggle the side navigation */}
      <button className={styles.menuBtn} onClick={toggleOpen}>
        {open ? (
          <KeyboardDoubleArrowLeftIcon />
        ) : (
          <KeyboardDoubleArrowRightIcon />
        )}
      </button>
      {/* Rendering navigation links using NavLink from react-router-dom */}
      {navData.map((item) => {
        return (
          <NavLink key={item.id} className={styles.sideitem} to={item.link}>
            {item.icon}
            <span className={styles.linkText}>{item.text}</span>
          </NavLink>
        );
      })}
    </div>
  );
}
