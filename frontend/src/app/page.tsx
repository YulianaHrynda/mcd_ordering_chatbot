import Link from 'next/link';
import { Box, Paper, Typography, Button, Stack } from '@mui/material';
import FastfoodIcon from '@mui/icons-material/Fastfood';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

export default function Home() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Paper elevation={6} sx={{ p: 6, borderRadius: 4, minWidth: 340, bgcolor: 'background.paper', textAlign: 'center' }}>
        <Typography variant="h3" fontWeight={700} color="primary" mb={2}>
          <FastfoodIcon fontSize="large" sx={{ verticalAlign: 'middle', mr: 1 }} />
          McDonald's Ordering Simulator
        </Typography>
        <Stack spacing={3} mt={4} mb={2}>
          <Button
            component={Link}
            href="/chat"
            variant="contained"
            color="primary"
            size="large"
            startIcon={<FastfoodIcon />}
            sx={{ fontWeight: 600, fontSize: 18, borderRadius: 3 }}
            fullWidth
          >
            🗨️ Order Chat
          </Button>
          <Button
            component={Link}
            href="/admin"
            variant="outlined"
            color="secondary"
            size="large"
            startIcon={<AdminPanelSettingsIcon />}
            sx={{ fontWeight: 600, fontSize: 18, borderRadius: 3 }}
            fullWidth
          >
            🛠️ Admin Panel
          </Button>
        </Stack>
        <Typography variant="body1" color="secondary" mt={2}>
          Welcome! Choose <b>Order Chat</b> to simulate a customer order, or <b>Admin Panel</b> to view all orders.
        </Typography>
      </Paper>
    </Box>
  );
}
