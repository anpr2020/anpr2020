import React from "react";

import { withStyles } from "@material-ui/core/styles";
import {
  Button,
  Container,
  FormControl,
  InputLabel,
  TextField,
  Typography,
  Switch,
  MenuItem,
  Select,
  Grid,
} from "@material-ui/core";
import VideocamIcon from "@material-ui/icons/Videocam";

const styles = {
  formControl: {
    minWidth: 120,
  },
};

class Live extends React.Component {
  constructor(props) {
    super(props);
    this.select = React.createRef();
    this.videoSource = React.createRef();
    this.state = {
      sourceSwitch: false,
      ipSwitch: false,
      sourceType: false,
      selectOptions: [],
      selectValue: "",
      streamSource: "",
      sourceValue: "",
      sourceUrl: "",
      sourceIP: "",
      sourcePort: 0,
    };
  }

  stopMediaTracks = (stream) => {
    const streamTracks = stream.getTracks();
    streamTracks.forEach((track) => {
      track.stop();
    });
  };

  gotDevices = (mediaDevices) => {
    let selectOptions = this.state.selectOptions || [];
    if (selectOptions.length === 0)
      mediaDevices.forEach((mediaDevice, i) => {
        if (mediaDevice.kind === "videoinput") {
          selectOptions.push(
            <MenuItem key={i} value={mediaDevice.deviceId || i}>
              {mediaDevice.label || `Camera ${i}`}
            </MenuItem>
          );
        }
      });
    this.setState({
      selectOptions: selectOptions || "",
    });
  };

  onChangeLiveSource = () => {
    const {
      sourceSwitch,
      streamSource,
      selectValue,
      sourceValue,
    } = this.state;

    if (sourceSwitch) {
      this.videoSource.current.src = sourceValue;
    } else {
      if (!selectValue) return;
      if (streamSource) this.stopMediaTracks(streamSource);

      const constraints = {
        video: {
          deviceId: { exact: selectValue },
        },
        audio: false,
      };

      navigator.mediaDevices
        .getUserMedia(constraints)
        .then((stream) => {
          this.setState({
            streamSource: stream,
          });
          this.videoSource.current.srcObject = stream;
        })
        .catch((error) => {
          console.error(error);
        });
    }
  };

  componentDidMount() {
    try {
      navigator.getUserMedia =
        navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.msGetUserMedia ||
        navigator.oGetUserMedia;
      if (!navigator.getUserMedia) return alert("No streaming devices found");
      navigator.mediaDevices.enumerateDevices().then(this.gotDevices);
    } catch (err) {
      alert("ERROR : " + err.message);
      console.log(err);
    }
  }

  handleSelectChange = (e) => {
    const selectValue = e.target.value;
    this.setState(
      {
        selectValue: selectValue,
      },
      () => this.onChangeLiveSource()
    );
  };

  handleSwitchChange = (e) =>
    this.setState({ [e.target.name]: e.target.checked });

  handleSourceInput = (e) => {
    const { sourceIP, sourcePort } = this.state;
    const { name, value } = e.target;

    this.setState(
      {
        [name]: value,
      },
      () => {
        this.setState(
          {
            sourceValue: ["sourceIP", "sourcePort"].includes(name)
              ? `http://${sourceIP}:${sourcePort}`
              : value,
          },
          () => this.onChangeLiveSource()
        );
      }
    );
  };

  render() {
    const { classes } = this.props;
    const {
      sourceSwitch,
      sourceType,
      ipSwitch,
      selectOptions,
      selectValue,
      sourceValue,
      sourceUrl,
      sourceIP,
      sourcePort,
    } = this.state;

    return (
      <Container maxWidth="xl">
        <Grid
          container
          spacing={3}
          justify="center"
          alignItems="center"
          style={{ textAlign: "center" }}
        >
          <Grid item md={3}>
            <FormControl variant="outlined" className={classes.formControl}>
              <InputLabel id="source-select-label">Source</InputLabel>
              <Select
                labelId="source-select-label"
                id="source-select"
                value={selectValue || ""}
                onChange={this.handleSelectChange}
                label="Source"
                ref={this.select}
                disabled={sourceSwitch}
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {selectOptions}
              </Select>
            </FormControl>
          </Grid>
          <Grid item md={2}>
            <Typography component="div">
              <Grid container justify="center" alignItems="center">
                <Grid item>Devices</Grid>
                <Grid item>
                  <Switch
                    name="sourceSwitch"
                    checked={sourceSwitch}
                    onChange={this.handleSwitchChange}
                  />
                </Grid>
                <Grid item>URL/IP:Port</Grid>
              </Grid>
            </Typography>
          </Grid>
          <Grid item md={7}>
            <Grid container justify="center" alignItems="center">
              <Grid item xs={12}>
                {ipSwitch ? (
                  <TextField
                    name="sourceUrl"
                    label="Source URL"
                    disabled={!sourceSwitch}
                    value={sourceUrl}
                    onChange={this.handleSourceInput}
                  />
                ) : (
                  <Grid container justify="center" alignItems="center">
                    <Grid item xs={8}>
                      <TextField
                        name="sourceIP"
                        label="IP"
                        disabled={!sourceSwitch}
                        value={sourceIP}
                        onChange={this.handleSourceInput}
                      />
                    </Grid>
                    <Grid item xs={4}>
                      <TextField
                        type="number"
                        name="sourcePort"
                        label="Port"
                        disabled={!sourceSwitch}
                        value={sourcePort}
                        onChange={this.handleSourceInput}
                      />
                    </Grid>
                  </Grid>
                )}
              </Grid>
              <Grid item xs={6}>
                <Typography component="div">
                  <Grid container justify="center" alignItems="center">
                    <Grid item>IP:Port</Grid>
                    <Grid item>
                      <Switch
                        name="ipSwitch"
                        checked={ipSwitch}
                        onChange={this.handleSwitchChange}
                        disabled={!sourceSwitch}
                      />
                    </Grid>
                    <Grid item>URL</Grid>
                  </Grid>
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography component="div">
                  <Grid container justify="center" alignItems="center">
                    <Grid item>Video</Grid>
                    <Grid item>
                      <Switch
                        name="sourceType"
                        checked={sourceType}
                        onChange={this.handleSwitchChange}
                        disabled={!sourceSwitch}
                      />
                    </Grid>
                    <Grid item>Image</Grid>
                  </Grid>
                </Typography>
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={12}>
            {sourceType ? (
              <img
                width="100%"
                key={0}
                alt=""
                ref={this.videoSource}
                src={sourceValue}
              />
            ) : (
              <video
                width="100%"
                key={0}
                ref={this.videoSource}
                autoPlay
                controls
              ></video>
            )}
          </Grid>
          <Grid item xs={12}>
            <Button
              size="large"
              variant="contained"
              color="primary"
              startIcon={<VideocamIcon />}
            >
              Start Streaming
            </Button>
          </Grid>
        </Grid>
      </Container>
    );
  }
}

export default withStyles(styles)(Live);
