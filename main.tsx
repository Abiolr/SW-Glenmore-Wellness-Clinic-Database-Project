import React from "react";
import ReactDOM from "react-dom/client";
import ClinicApp from "./ClinicApp";

const rootElement = document.getElementById("root");
if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <ClinicApp />
    </React.StrictMode>
  );
} else {
  throw new Error('Root element not found');
}
