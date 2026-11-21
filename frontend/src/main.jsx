import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { ScanProvider } from "./context/ScanContext.jsx";
import "./index.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <ScanProvider>
        <App />
      </ScanProvider>
    </BrowserRouter>
  </React.StrictMode>
);
