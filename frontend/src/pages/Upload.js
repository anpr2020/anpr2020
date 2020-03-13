import React from "react";
import { Redirect } from "react-router-dom";
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  FormControl,
  Input,
  CircularProgress,
} from "@material-ui/core";

import SrcCard from "../components/SrcCard";
import DataTable from "../components/DataTable";

export default class Upload extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      formState: "INPUT",
      formResult: null,
      fileObject: null,
      src: null,
    };
  }

  getTaskId = async (formData) => {
    return await (
      await fetch(window.djangoUrls.Process, {
        method: "POST",
        body: formData,
      })
    ).json();
  };

  handleSubmit = (event) => {
    event.preventDefault();
    const { fileObject } = this.state;

    if (!fileObject) return alert("Please choose a file to upload");

    this.setState({
      formState: "SUBMIT",
    });

    const formData = new FormData();

    formData.append("video_file", fileObject);

    this.getTaskId(formData).then((response) => {
      this.setState({
        formState: "RESULT",
        formResult: response,
      });
    });
  };

  handleChange = (event) => {
    const fileObject = event.target.files[0] || null;
    this.state.fileObject !== fileObject &&
      this.setState({
        fileObject: fileObject,
        src: this.getBlobUrl(fileObject),
      });
  };

  getBlobUrl(fileObject) {
    return fileObject ? URL.createObjectURL(fileObject) : null;
  }

  render() {
    const { formState, formResult } = this.state;
    var cardContent;

    if (formState === "INPUT") {
      cardContent = (
        <React.Fragment>
          <Typography variant="h6">Upload Video</Typography>
          <form onSubmit={this.handleSubmit}>
            <Box p={5}>
              <FormControl>
                <Input type="file" onChange={this.handleChange} />
              </FormControl>
            </Box>
            <Button
              variant="contained"
              color="secondary"
              size="large"
              type="submit"
            >
              Upload
            </Button>
          </form>
        </React.Fragment>
      );
    } else if (formState === "SUBMIT") {
      cardContent = (
        <React.Fragment>
          <Typography variant="h2">Uploading...</Typography>
          <CircularProgress />
        </React.Fragment>
      );
    } else if (formState === "RESULT" && formResult) {
      cardContent = (
        <Redirect to={window.urls.Progress.toUrl({ id: formResult.task_id })} />
      );
    }

    return (
      <React.Fragment>
        <Box m={3} textAlign="center">
          <Card>
            <CardContent>{cardContent}</CardContent>
          </Card>
        </Box>
        <SrcCard src={this.state.src} />
      </React.Fragment>
    );
  }
}
