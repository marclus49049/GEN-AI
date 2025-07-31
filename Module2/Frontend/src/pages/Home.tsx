import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Grid,
  Typography,
} from '@mui/material';
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ROUTES } from '../utils/constants';

export const Home: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to Todo App
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Organize your tasks efficiently with public and private todos
        </Typography>
      </Box>

      <Grid container spacing={4} justifyContent="center">
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h4" component="h2" gutterBottom>
                Public Todos
              </Typography>
              <Typography variant="body1" paragraph>
                Share and collaborate on tasks with everyone. No account needed
                to create or view public todos.
              </Typography>
              <Button
                variant="contained"
                component={RouterLink}
                to={ROUTES.PUBLIC_TODOS}
                fullWidth
              >
                Browse Public Todos
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h4" component="h2" gutterBottom>
                Private Todos
              </Typography>
              <Typography variant="body1" paragraph>
                Keep your personal tasks secure and private. Create an account
                to manage your own todo list.
              </Typography>
              {isAuthenticated ? (
                <Button
                  variant="contained"
                  component={RouterLink}
                  to={ROUTES.PRIVATE_TODOS}
                  fullWidth
                >
                  Go to My Todos
                </Button>
              ) : (
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    component={RouterLink}
                    to={ROUTES.LOGIN}
                    fullWidth
                  >
                    Login
                  </Button>
                  <Button
                    variant="outlined"
                    component={RouterLink}
                    to={ROUTES.REGISTER}
                    fullWidth
                  >
                    Register
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 8, textAlign: 'center' }}>
        <Typography variant="h6" gutterBottom>
          Features
        </Typography>
        <Grid container spacing={2} justifyContent="center">
          <Grid item xs={12} sm={4}>
            <Typography variant="body1">✓ Simple and intuitive</Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="body1">✓ Secure authentication</Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="body1">✓ Real-time updates</Typography>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};