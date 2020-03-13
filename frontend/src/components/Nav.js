import React from "react";
import { Link } from "react-router-dom";

import { Box, ButtonGroup, Button } from "@material-ui/core";

export default function Nav() {
  return (
    <Box
      my={3}
      style={{
        textAlign: "center",
      }}
    >
      <ButtonGroup
        className="align-center"
        size="large"
        color="primary"
        aria-label="large outlined primary button group"
      >
        <Button component={Link} to={window.urls.Upload.path}>
          Upload
        </Button>
        <Button component={Link} to={window.urls.Live.path}>
          Live
        </Button>
      </ButtonGroup>
    </Box>
  );
}
