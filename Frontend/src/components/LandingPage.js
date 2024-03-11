import { Box, Button, Grid, Typography } from '@mui/material';
import { EditCalendarIcon, InfoIcon } from '@mui/icons-material';
import { createTheme, responsiveFontSizes, ThemeProvider } from '@mui/material/styles';
import '../styles/LandingPage.css';

const theme = responsiveFontSizes(createTheme());

const LandingPage = () => {
  return (
    <ThemeProvider theme={theme}>
      <Box className="landing-page" sx={{ marginBottom: '125px' }}>
        <Typography variant="h2" sx={{ marginBottom: '100px' }}>
          Welcome to the Carleton University
          <br />
          Student Scheduler Tool
        </Typography>
        <Grid container spacing={4} justifyContent="center" alignItems="center">
          <Grid item>
            <Button
              href="#form-component"
              variant="outlined"
              sx={{
                borderColor: 'white',
                color: 'white',
                transition: 'opacity 0.3s ease-in-out',
                '&:hover': {
                  opacity: '0.7',
                  borderColor: 'white',
                },
              }}
              size="large"
              startIcon={<EditCalendarIcon />}
            >
              Build Your Schedule
            </Button>
          </Grid>
          {/* Add space between buttons */}
          <Grid item>
            <Button
              href="https://carleton.ca/"
              target="_blank"
              variant="outlined"
              sx={{
                borderColor: 'white',
                color: 'white',
                transition: 'opacity 0.3s ease-in-out',
                '&:hover': {
                  opacity: '0.7',
                  borderColor: 'white',
                },
              }}
              size="large"
              startIcon={<InfoIcon />}
            >
              Need Assistance
            </Button>
          </Grid>
        </Grid>
      </Box>
    </ThemeProvider>
  );
};

export default LandingPage;