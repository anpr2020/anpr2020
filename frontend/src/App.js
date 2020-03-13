import React from "react";
import { Redirect, Switch, Route } from "react-router-dom";

import Layout from "./components/Layout";

import Upload from "./pages/Upload";
import Live from "./pages/Live";
import Progress from "./pages/Progress";

import "./urls";

function App() {
  return (
    <Layout>
      <Switch>
        <Redirect exact from="/" to={window.urls.Upload.path} />
        <Route path={window.urls.Upload.path} component={Upload} />
        <Route path={window.urls.Live.path} component={Live} />
        <Route path={window.urls.Progress.path} component={Progress} />
      </Switch>
    </Layout>
  );
}

export default App;
