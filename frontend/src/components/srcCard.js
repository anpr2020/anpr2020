import React from "react";

import { Box, Card, CardContent, Typography } from "@material-ui/core";

export default class SrcCard extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      src: this.props.src
    };
  }

  componentWillReceiveProps(newProps) {
    if (newProps.src !== this.props.src) {
      this.setState({
        src: newProps.src
      });
    }
  }

  render() {
    const { src } = this.state;

    return (
      <Box m={3} textAlign='center'>
        <Card>
          <CardContent>
            {src ? (
              <video key={src} height="100%" width="100%" controls>
                <source src={src} />
              </video>
            ) : (
              <Typography variant="h5" align="center">
                Choose a video to see preview
              </Typography>
            )}
          </CardContent>
        </Card>
      </Box>
    );
  }
}
