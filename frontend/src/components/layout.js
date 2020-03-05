import React from "react";
import { CssBaseline, Container } from "@material-ui/core";

import Seo from './seo'
import Header from "./header";

export default function Layout(props) {
  return (
    <React.Fragment>
			<CssBaseline/>
			<Seo seo={props.seo} />
      <Header />
      <Container>{props.children}</Container>
      <footer></footer>
    </React.Fragment>
  );
}
