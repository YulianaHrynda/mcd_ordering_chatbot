import React from 'react';
import { Box, Paper, Typography, Divider } from '@mui/material';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

export default function AdminPanel() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Paper elevation={6} sx={{ p: 6, borderRadius: 4, minWidth: 400, bgcolor: 'background.paper', width: '100%', maxWidth: 700 }}>
        <Typography variant="h4" fontWeight={700} color="primary" mb={2}>
          <AdminPanelSettingsIcon fontSize="large" sx={{ verticalAlign: 'middle', mr: 1 }} />
          Admin Panel
        </Typography>
        <Divider sx={{ mb: 3, bgcolor: 'grey.800' }} />
        <Typography variant="body1" color="secondary" mb={2}>
          This page will show all orders placed by users.
        </Typography>
        <Box sx={{ border: '1px solid', borderColor: 'grey.800', minHeight: 300, borderRadius: 3, bgcolor: 'background.default', p: 2 }}>
          <Typography color="secondary">Order list will appear here.</Typography>
        </Box>
      </Paper>
    </Box>
  );
} 