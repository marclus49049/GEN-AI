import { Delete, Edit } from '@mui/icons-material';
import {
  Box,
  Checkbox,
  Chip,
  IconButton,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
} from '@mui/material';
import React from 'react';
import { PublicTodo, Todo } from '../../types';
import { formatDate } from '../../utils/helpers';

interface TodoItemProps {
  todo: Todo | PublicTodo;
  onToggle?: (id: number, completed: boolean) => void;
  onEdit?: (todo: Todo | PublicTodo) => void;
  onDelete?: (id: number) => void;
  readOnly?: boolean;
}

export const TodoItem: React.FC<TodoItemProps> = ({
  todo,
  onToggle,
  onEdit,
  onDelete,
  readOnly = false,
}) => {
  const handleToggle = () => {
    if (onToggle && !readOnly) {
      onToggle(todo.id, !todo.completed);
    }
  };

  return (
    <ListItem
      secondaryAction={
        !readOnly && (
          <Box>
            {onEdit && (
              <IconButton
                edge="end"
                aria-label="edit"
                onClick={() => onEdit(todo)}
                sx={{ mr: 1 }}
              >
                <Edit />
              </IconButton>
            )}
            {onDelete && (
              <IconButton
                edge="end"
                aria-label="delete"
                onClick={() => onDelete(todo.id)}
              >
                <Delete />
              </IconButton>
            )}
          </Box>
        )
      }
      sx={{
        bgcolor: 'background.paper',
        mb: 1,
        borderRadius: 1,
        '&:hover': {
          bgcolor: 'action.hover',
        },
      }}
    >
      <ListItemIcon>
        <Checkbox
          edge="start"
          checked={todo.completed}
          onChange={handleToggle}
          disabled={readOnly}
        />
      </ListItemIcon>
      <ListItemText
        primary={
          <Typography
            variant="body1"
            sx={{
              textDecoration: todo.completed ? 'line-through' : 'none',
              color: todo.completed ? 'text.secondary' : 'text.primary',
            }}
          >
            {todo.title}
          </Typography>
        }
        secondary={
          <>
            {todo.description && (
              <Typography variant="body2" color="text.secondary">
                {todo.description}
              </Typography>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                Created: {formatDate(todo.created_at)}
              </Typography>
              <Chip
                label={todo.is_public ? 'Public' : 'Private'}
                size="small"
                color={todo.is_public ? 'primary' : 'default'}
                variant="outlined"
                sx={{ height: 18, fontSize: '0.6rem' }}
              />
            </Box>
          </>
        }
      />
    </ListItem>
  );
};