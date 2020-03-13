import React from "react";
import { Link as RouterLink } from "react-router-dom";

import { Link, Button } from "@material-ui/core";

export default function CustomButton({ href, children }, props) {
  return (
    <Button component={RouterLink} to={href} {...props}>
      {children}
    </Button>
  );
}
