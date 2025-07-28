'use client';

import React, { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import {
  Box, Button, TextField, Typography, Avatar, List, ListItem, ListItemAvatar, ListItemText, Badge, Paper, Divider, IconButton, Stack, ListItemButton, CssBaseline
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import PersonIcon from '@mui/icons-material/Person';
import FastfoodIcon from '@mui/icons-material/Fastfood';
import AddIcon from '@mui/icons-material/Add';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#22c55e' }, // green accent for user
    background: { default: '#18181b', paper: '#232329' },
    secondary: { main: '#a1a1aa' },
  },
  shape: { borderRadius: 16 },
});

interface Message {
  sender: 'user' | 'system';
  text: string;
  llm?: boolean;
}

interface ChatSession {
  id: string;
  name: string;
  session_id: string;
  messages: Message[];
  isLoading: boolean;
  finalized: boolean;
  orderSummary?: {
    order_id: string;
    items: { name: string; type: string; size?: string; price?: number }[];
    total: number;
  };
}

export default function ChatPage() {
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const chatWindowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [activeChat, chats]);

  // Create a new chat session
  const handleNewChat = () => {
    const id = uuidv4();
    const newChat: ChatSession = {
      id,
      name: `Chat ${chats.length + 1}`,
      session_id: '',
      messages: [],
      isLoading: false,
      finalized: false,
    };
    setChats(prev => [...prev, newChat]);
    setActiveChat(id);
    setInput('');
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  // Send a message in the active chat
  const handleSend = async () => {
    if (!input.trim() || !activeChat) return;
    setChats(prev => prev.map(chat =>
      chat.id === activeChat
        ? { ...chat, messages: [...chat.messages, { sender: 'user', text: input }], isLoading: true }
        : chat
    ));
    setInput('');
    setTimeout(() => inputRef.current?.focus(), 100);

    const chat = chats.find(c => c.id === activeChat);
    if (!chat) return;
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: chat.session_id || undefined,
          message: input
        })
      });
      const data = await res.json();
      setChats(prev => prev.map(c => {
        if (c.id !== activeChat) return c;
        const newMessages = [...c.messages, { sender: 'system', text: data.response, llm: true }];
        return {
          ...c,
          session_id: data.session_id,
          messages: newMessages,
          isLoading: false,
          finalized: data.finalized,
          orderSummary: data.order || c.orderSummary
        };
      }));
    } catch (e) {
      setChats(prev => prev.map(c =>
        c.id === activeChat
          ? {
              ...c,
              messages: [...c.messages, { sender: 'system', text: 'Error: Could not reach backend.', llm: false }],
              isLoading: false
            }
          : c
      ));
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ p: { xs: 1, md: 4 }, height: '100vh', bgcolor: 'background.default' }}>
        <Typography variant="h4" fontWeight={700} mb={2} textAlign="center" color="primary">
          <FastfoodIcon fontSize="large" color="primary" sx={{ verticalAlign: 'middle', mr: 1 }} />
          McDonald's Order Chat
        </Typography>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={3} sx={{ height: { md: '80vh' } }}>
          {/* Chat List */}
          <Paper elevation={3} sx={{ minWidth: 220, maxWidth: 260, p: 2, height: { md: '100%' }, mb: { xs: 2, md: 0 }, bgcolor: 'background.paper' }}>
            <Typography variant="h6" mb={1} color="secondary.light">
              <ChatBubbleOutlineIcon sx={{ mr: 1 }} />Chats
            </Typography>
            <List>
              {chats.map(chat => (
                <ListItem disablePadding key={chat.id}>
                  <ListItemButton
                    selected={chat.id === activeChat}
                    onClick={() => setActiveChat(chat.id)}
                    sx={{ borderRadius: 2, mb: 1, bgcolor: chat.id === activeChat ? 'primary.dark' : undefined }}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: chat.id === activeChat ? 'primary.main' : 'grey.800' }}>
                        <FastfoodIcon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText primary={chat.name} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              fullWidth
              sx={{ mt: 2 }}
              onClick={handleNewChat}
            >
              New Chat
            </Button>
          </Paper>
          {/* Chat Window */}
          <Paper elevation={3} sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 2, minHeight: 400, bgcolor: 'background.paper' }}>
            {activeChat ? (
              <>
                <Typography variant="h6" mb={1} color="secondary.light">
                  {chats.find(c => c.id === activeChat)?.name}
                </Typography>
                <Divider sx={{ mb: 1, bgcolor: 'grey.800' }} />
                <Box
                  ref={chatWindowRef}
                  sx={{ flex: 1, overflowY: 'auto', mb: 2, p: 1, bgcolor: 'background.default', borderRadius: 2, minHeight: 300, maxHeight: { xs: 300, md: 500 } }}
                >
                  {chats.find(c => c.id === activeChat)?.messages.map((msg, idx) => (
                    <Box
                      key={idx}
                      display="flex"
                      flexDirection={msg.sender === 'user' ? 'row-reverse' : 'row'}
                      alignItems="flex-end"
                      mb={2}
                    >
                      <Avatar sx={{ bgcolor: msg.sender === 'user' ? 'primary.main' : 'grey.700', ml: msg.sender === 'user' ? 2 : 0, mr: msg.sender === 'system' ? 2 : 0 }}>
                        {msg.sender === 'user' ? <PersonIcon /> : <FastfoodIcon />}
                      </Avatar>
                      <Box>
                        <Paper
                          elevation={4}
                          sx={{
                            p: 2,
                            bgcolor: msg.sender === 'user' ? 'primary.main' : 'grey.900',
                            color: msg.sender === 'user' ? '#fff' : 'grey.100',
                            borderRadius: 3,
                            minWidth: 80,
                            maxWidth: { xs: 260, md: 480 },
                            wordBreak: 'break-word',
                            position: 'relative',
                            boxShadow: msg.sender === 'user' ? '0 2px 8px #22c55e33' : '0 2px 8px #0002',
                            mb: 0.5,
                          }}
                        >
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {msg.text}
                          </Typography>
                          {msg.llm && (
                            <Badge
                              color="secondary"
                              badgeContent="LLM"
                              sx={{ position: 'absolute', top: -10, right: -10 }}
                            />
                          )}
                        </Paper>
                      </Box>
                    </Box>
                  ))}
                  {chats.find(c => c.id === activeChat)?.isLoading && (
                    <Typography color="secondary" fontStyle="italic" mt={1}>
                      System is typing...
                    </Typography>
                  )}
                  {/* Show order summary if finalized */}
                  {chats.find(c => c.id === activeChat)?.finalized && chats.find(c => c.id === activeChat)?.orderSummary && (
                    <Box mt={3} p={2} bgcolor="grey.900" borderRadius={2}>
                      <Typography variant="h6" color="primary">Order Summary</Typography>
                      <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                        {chats.find(c => c.id === activeChat)?.orderSummary?.items.map((item, idx) => (
                          <li key={idx} style={{ marginBottom: 4 }}>
                            <Typography color="secondary">{item.name} {item.size ? `(${item.size})` : ''} - ${item.price?.toFixed(2) ?? ''}</Typography>
                          </li>
                        ))}
                      </ul>
                      <Typography variant="body1" color="primary" fontWeight={700} mt={1}>
                        Total: ${chats.find(c => c.id === activeChat)?.orderSummary?.total.toFixed(2)}
                      </Typography>
                    </Box>
                  )}
                </Box>
                <Box display="flex" alignItems="center" gap={1}>
                  <TextField
                    inputRef={inputRef}
                    fullWidth
                    placeholder="Type your message..."
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleInputKeyDown}
                    disabled={chats.find(c => c.id === activeChat)?.isLoading || chats.find(c => c.id === activeChat)?.finalized}
                    size="small"
                    sx={{ bgcolor: 'grey.900', borderRadius: 2, color: '#fff' }}
                  />
                  <IconButton
                    color="primary"
                    onClick={handleSend}
                    disabled={chats.find(c => c.id === activeChat)?.isLoading || !input.trim() || chats.find(c => c.id === activeChat)?.finalized}
                    sx={{ bgcolor: 'primary.main', color: '#fff', '&:hover': { bgcolor: 'primary.dark' } }}
                  >
                    <SendIcon />
                  </IconButton>
                </Box>
              </>
            ) : (
              <Box display="flex" flex={1} alignItems="center" justifyContent="center" minHeight={300}>
                <Typography color="secondary">Select a chat or start a new one.</Typography>
              </Box>
            )}
          </Paper>
        </Stack>
      </Box>
    </ThemeProvider>
  );
}

function SendIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M2 21L23 12L2 3V10L17 12L2 14V21Z" fill="currentColor" />
    </svg>
  );
} 