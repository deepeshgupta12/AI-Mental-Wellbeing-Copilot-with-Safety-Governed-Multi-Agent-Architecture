import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./index.css";
import { AppQueryProvider } from "./providers/query-provider";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppQueryProvider>
      <App />
    </AppQueryProvider>
  </React.StrictMode>,
);