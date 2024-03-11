import { Box, Button, Grid, Typography } from '@mui/material';
import { createTheme, responsiveFontSizes, ThemeProvider } from '@mui/material/styles';
import { GitHubIcon } from '@mui/icons-material';
import '../styles/Footer.css';

const theme = responsiveFontSizes(createTheme());

const Footer = () => {
    return (
        <ThemeProvider theme={theme}>
            <Box className="footer">
                <Grid container justifyContent="space-between" alignItems="center" spacing={2}>
                    <Grid item xs={12} sm={6}>
                        <Typography align="left">
                            &copy; 2024 CarletonClassScheduler. All rights reserved.
                        </Typography>
                    </Grid>
                    <Grid item xs={12} sm="auto" container justifyContent="center" style={{ textAlign: 'right' }}>
                        <Button
                            href="https://github.com/ConnorMarcus/CarletonClassScheduler"
                            target="_blank"
                            variant="outlined"
                            size="medium"
                            sx={{
                                color: 'black',
                                borderColor: 'black',
                                transition: 'opacity 0.3s ease-in-out',
                                maxWidth: 'fit-content',
                                '&:hover': {
                                    opacity: 0.7,
                                    borderColor: 'black'
                                },
                                alignContent: 'right',
                            }}
                            startIcon={<GitHubIcon />}
                        >
                            View on GitHub
                        </Button>
                    </Grid>
                </Grid>
            </Box>
        </ThemeProvider>
    );
};

export default Footer;