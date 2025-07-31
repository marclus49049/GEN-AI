import {
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Notifications as NotificationsIcon,
  NotificationsNone as NotificationsNoneIcon
} from '@mui/icons-material';
import {
  Avatar,
  Badge,
  Box,
  Button,
  Chip,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Popover,
  Typography
} from '@mui/material';
import { formatDistanceToNow } from 'date-fns';
import React, { useState } from 'react';
import { useNotifications } from '../../contexts/NotificationContext';

const getActionIcon = (actionType: string) => {
  switch (actionType) {
    case 'updated':
      return <EditIcon fontSize="small" />;
    case 'deleted':
      return <DeleteIcon fontSize="small" />;
    case 'completed':
      return <CheckCircleIcon fontSize="small" />;
    default:
      return <EditIcon fontSize="small" />;
  }
};

const getActionColor = (actionType: string) => {
  switch (actionType) {
    case 'updated':
      return 'primary';
    case 'deleted':
      return 'error';
    case 'completed':
      return 'success';
    default:
      return 'default';
  }
};

export const NotificationBell: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const { notifications, unreadCount, isConnected, markAsRead, markAllAsRead } = useNotifications();

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = async (notification: any) => {
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }
  };

  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  const open = Boolean(anchorEl);
  const id = open ? 'notification-popover' : undefined;

  return (
    <>
      <IconButton
        color="inherit"
        onClick={handleClick}
        sx={{
          position: 'relative',
          mr: 1,
        }}
      >
        <Badge badgeContent={unreadCount} color="error" max={99}>
          {unreadCount > 0 ? <NotificationsIcon /> : <NotificationsNoneIcon />}
        </Badge>
        {/* Connection status indicator */}
        {isConnected && (
          <Box
            sx={{
              position: 'absolute',
              bottom: 2,
              right: 2,
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: 'success.main',
              border: '1px solid white',
            }}
          />
        )}
      </IconButton>

      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: {
            width: 400,
            maxHeight: 500,
            overflow: 'hidden',
          },
        }}
      >
        <Box>
          {/* Header */}
          <Box
            sx={{
              p: 2,
              borderBottom: 1,
              borderColor: 'divider',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Typography variant="h6">
              Notifications
              {unreadCount > 0 && (
                <Chip
                  label={unreadCount}
                  size="small"
                  color="error"
                  sx={{ ml: 1 }}
                />
              )}
            </Typography>
            {unreadCount > 0 && (
              <Button
                size="small"
                onClick={handleMarkAllAsRead}
                sx={{ textTransform: 'none' }}
              >
                Mark all read
              </Button>
            )}
          </Box>

          {/* Connection Status */}
          <Box
            sx={{
              px: 2,
              py: 1,
              bgcolor: isConnected ? 'success.light' : 'warning.light',
              color: isConnected ? 'success.contrastText' : 'warning.contrastText',
            }}
          >
            <Typography variant="caption">
              {isConnected ? '🟢 Live notifications active' : '🟡 Connecting...'}
            </Typography>
          </Box>

          {/* Notifications List */}
          <Box sx={{ maxHeight: 350, overflow: 'auto' }}>
            {notifications.length === 0 ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <NotificationsNoneIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  No notifications yet
                </Typography>
              </Box>
            ) : (
              <List sx={{ p: 0 }}>
                {notifications.map((notification, index) => (
                  <React.Fragment key={notification.id}>
                    <ListItem
                      button
                      onClick={() => handleNotificationClick(notification)}
                      sx={{
                        bgcolor: notification.is_read ? 'transparent' : 'action.hover',
                        '&:hover': {
                          bgcolor: 'action.selected',
                        },
                      }}
                    >
                      <ListItemAvatar>
                        <Avatar
                          sx={{
                            bgcolor: `${getActionColor(notification.action_type)}.light`,
                            color: `${getActionColor(notification.action_type)}.contrastText`,
                            width: 36,
                            height: 36,
                          }}
                        >
                          {getActionIcon(notification.action_type)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography
                              variant="body2"
                              sx={{
                                fontWeight: notification.is_read ? 'normal' : 'bold',
                                lineHeight: 1.3,
                              }}
                            >
                              {notification.message}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                              <Typography variant="caption" color="text.secondary">
                                {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                              </Typography>
                              {notification.actor_username && (
                                <Chip
                                  label={notification.actor_username}
                                  size="small"
                                  variant="outlined"
                                  sx={{ height: 16, fontSize: '0.65rem' }}
                                />
                              )}
                              {!notification.is_read && (
                                <Box
                                  sx={{
                                    width: 6,
                                    height: 6,
                                    borderRadius: '50%',
                                    backgroundColor: 'primary.main',
                                  }}
                                />
                              )}
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < notifications.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Box>

          {notifications.length > 0 && (
            <Box
              sx={{
                p: 1,
                borderTop: 1,
                borderColor: 'divider',
                textAlign: 'center',
              }}
            >
              <Button
                size="small"
                onClick={handleClose}
                sx={{ textTransform: 'none' }}
              >
                Close
              </Button>
            </Box>
          )}
        </Box>
      </Popover>
    </>
  );
};