import React from "react";
import {
  AppBar,
  Toolbar,
  Typography
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1
  },
  menuButton: {
    marginRight: theme.spacing(2)
  },
  title: {
    flexGrow: 1
  }
}));

export default function Header() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" align="center" className={classes.title}>
            Multiple Vehicle Automatic Number Plate Recognition
          </Typography>
        </Toolbar>
      </AppBar>
    </div>
  );
}
