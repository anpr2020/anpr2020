import React from "react";

import Layout from "./components/layout";

import Home from "./pages/home";

import djangoUrls from "./urls";

function App() {
  window.djangoUrls = djangoUrls;

  return (
    <Layout>
      <Home/>
    </Layout>
  );
}

export default App;
