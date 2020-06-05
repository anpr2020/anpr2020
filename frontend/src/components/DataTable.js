import React from "react";

import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@material-ui/core";

export default function DataTable({ data }) {
  return (
    <Box m={3}>
      <TableContainer component={Paper}>
        <Table size="small" aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Frame</TableCell>
              <TableCell>Extracted Text</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(data).map((rows, i) => (
              <TableRow key={i}>
                <TableCell>{rows[0]}</TableCell>
                <TableCell>{rows[1].join(", ")}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
