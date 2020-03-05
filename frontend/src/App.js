import React from "react";
import { Switch, Route } from "react-router-dom";

import Layout from "./components/layout";

import Home from "./pages/home";

import urls, { djangoUrls } from "./urls";

function App() {
  window.urls = urls;
  window.djangoUrls = djangoUrls;

  return (
    <Layout>
      <Switch>
        <Route path={window.urls.HomeLocation.path} component={Home} />
      </Switch>
    </Layout>
  );
}

export default App;
