import React from "react";

import { Container } from "@material-ui/core";

export default class Live extends React.Component {
	constructor(props){
		super(props);
		this.videoSource = React.createRef();
	}

	componentDidMount(){
		
	}

  render() {
    return (
      <Container maxWidth="xl">
        <video ref={this.videoSource} autoplay="true" />
      </Container>
    );
  }
}
