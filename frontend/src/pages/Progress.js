import React from "react";

import {
  Container,
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
} from "@material-ui/core";
import { withStyles } from "@material-ui/core/styles";

import DataTable from "../components/DataTable";

const styles = (theme) => ({
  canvasStyles: {
    width: "100%",
    height: "100%",
  },
});

class Progress extends React.Component {
  constructor(props) {
    super(props);
    this.frameCanvas = React.createRef();
    this.cannyCanvas = React.createRef();
    this.countourCanvas = React.createRef();
    this.outputCanvas = React.createRef();
    this.progressIndex = 0;
    this.state = {
      progressState: null,
      progressInfo: null,
      progressTable: {},
    };
  }

  setImage = (elRef, imageData) => {
    elRef.current.src = imageData;
  };

  doUpdate = () => {
    const { progressState, progressInfo } = this.state;
    if (["RUNNING", "SUCCESS"].includes(progressState) && progressInfo) {
      while (
        progressInfo.hasOwnProperty("frame") &&
        this.progressIndex < progressInfo.frame.length
      ) {
        this.setImage(this.frameCanvas, progressInfo.frame[this.progressIndex]);

        if (progressInfo.hasOwnProperty("canny")) {
          this.setImage(
            this.cannyCanvas,
            progressInfo.canny[this.progressIndex]
          );
        }
        if (progressInfo.hasOwnProperty("contour")) {
          this.setImage(
            this.countourCanvas,
            progressInfo.contour[this.progressIndex]
          );
        }
        if (progressInfo.hasOwnProperty("plate")) {
          this.setImage(
            this.outputCanvas,
            progressInfo.plate[this.progressIndex]
          );
        }
        this.progressIndex++;
      }
    }
  };

  componentDidMount() {
    const { id } = this.props.match.params;
    const { progressTable } = this.state;

    if (id) {
      const ws = new WebSocket(window.djangoUrls.Progress + id);

      window.console.log(window.djangoUrls.Progress + id, ws);
      ws.onmessage = (data) => {
        window.console.log(data);
        let dataTable = {},
          res = JSON.parse(data.data);
        if (res.info && res.info.hasOwnProperty("plate")) {
          res.info.plate.map((p, i) => {
            dataTable[i] = res.info.text[i];
          });
        }
        this.setState({
          progressState: res.state,
          progressInfo: res.info,
          progressTable: { ...progressTable, ...dataTable },
        });
        this.doUpdate();
        if (["PENDING", "START", "RUNNING"].includes(res.state)) {
          ws.send("ready");
        }
      };

      ws.onerror = (err) => {
        this.setState({
          progressState: "FAILURE",
          progressInfo: err.toString(),
        });
        alert("ERROR : " + err);
      };

      ws.onopen = () => ws.send("ready");
    }
  }

  render() {
    const { progressState, progressInfo, progressTable } = this.state;
    const { match, classes } = this.props;
    const { id } = match.params;

    let renderElement = () => {
      if ([null, "PENDING"].includes(progressState)) {
        return (
          <Box textAlign="center">
            <Typography component="h4">Processing Video</Typography>
            <CircularProgress />
          </Box>
        );
      } else if (["RUNNING", "SUCCESS"].includes(progressState)) {
        return (
          <Container maxWidth="xl">
            <Grid container spacing={1}>
              <Grid item xs={12}>
                <Typography variant="h2" align="center">
                  {progressState}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Box component={Paper}>
                  <Typography variant="subtitle2" align="center">
                    Frame Output
                  </Typography>
                  <img
                    alt=""
                    key={0}
                    ref={this.frameCanvas}
                    className={classes.canvasStyles}
                  />
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box component={Paper}>
                  <Typography variant="subtitle2" align="center">
                    Canny Output
                  </Typography>
                  <img
                    alt=""
                    key={1}
                    ref={this.cannyCanvas}
                    className={classes.canvasStyles}
                  />
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box component={Paper}>
                  <Typography variant="subtitle2" align="center">
                    Contour Output
                  </Typography>
                  <img
                    alt=""
                    key={2}
                    ref={this.countourCanvas}
                    className={classes.canvasStyles}
                  />
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box component={Paper}>
                  <Typography variant="subtitle2" align="center">
                    Recognition Output
                  </Typography>
                  <img
                    alt=""
                    key={3}
                    ref={this.outputCanvas}
                    className={classes.canvasStyles}
                  />
                </Box>
              </Grid>
              {progressState === "SUCCESS" && progressInfo.hasOwnProperty("platesFound") ? (
                <Grid item xs={12}>
                  <Box component={Paper}>
                    <Typography variant="subtitle2" align="center">
                      Plates Found
                    </Typography>
                    <Typography component="h4" variant="h4">
											{progressInfo.platesFound.length ? (
												progressInfo.platesFound.join(', ')
											) : ''}
										</Typography>
                  </Box>
                </Grid>
              ) : (
                ""
              )}
              <Grid item xs={12}>
                <Box component={Paper}>
                  <Typography variant="subtitle2" align="center">
                    Text Output
                  </Typography>
                  <DataTable data={progressTable} />
                </Box>
              </Grid>
            </Grid>
          </Container>
        );
      } else if (!id) {
        return <h1 className="text-center">No ID</h1>;
      } else {
        return (
          <div>
            <Typography variant="h2" align="center">
              STATE : {progressState}
            </Typography>
            <Typography variant="h2" align="center">
              INFO : {progressInfo}
            </Typography>
          </div>
        );
      }
    };

    return renderElement();
  }
}

export default withStyles(styles)(Progress);
