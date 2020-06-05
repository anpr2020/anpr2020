import React from "react";
import { CssBaseline, Container } from "@material-ui/core";

import Seo from "./Seo";
import Header from "./Header";
import Nav from "./Nav";

export default function Layout(props) {
  return (
    <React.Fragment>
      <CssBaseline />
      <Seo seo={props.seo} />
      <Header />
      <Nav />
      <Container>{props.children}</Container>
      <footer></footer>
    </React.Fragment>
  );
}
