import React from 'react';
import { Alert, AlertTitle, Box } from '@mui/material';

interface ErrorAlertProps {
  error: string | Error | unknown;
  title?: string;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, title = 'Error' }) => {
  const errorMessage = error instanceof Error ? error.message : String(error);

  return (
    <Box sx={{ mb: 2 }}>
      <Alert severity="error">
        <AlertTitle>{title}</AlertTitle>
        {errorMessage}
      </Alert>
    </Box>
  );
};