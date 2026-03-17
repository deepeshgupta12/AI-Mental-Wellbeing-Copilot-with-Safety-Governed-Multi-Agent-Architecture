import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import "./index.css";
import { AppQueryProvider } from "./providers/query-provider";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppQueryProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AppQueryProvider>
  </React.StrictMode>,
);