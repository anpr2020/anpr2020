import React from "react";
import { Helmet } from "react-helmet";

export default function Seo(props) {
  return (
    <Helmet defer={false}>
      <title>
        {props.title || "Multiple Vehicle Automatic Number Plate Recognition"}
      </title>
    </Helmet>
  );
}
