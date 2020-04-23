import React from "react";

import { Container } from "@material-ui/core";

export default class Live extends React.Component {
  constructor(props) {
    super(props);
    this.videoSource = React.createRef();
  }

  componentDidMount() {
    if (navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
          this.videoSource.current.srcObject = stream;
        })
        .catch((err) => {
          alert("ERROR " + err);
        });
    }
  }

  render() {
    return (
      <Container maxWidth="xl">
        <video width="100%" ref={this.videoSource} autoPlay />
      </Container>
    );
  }
}
