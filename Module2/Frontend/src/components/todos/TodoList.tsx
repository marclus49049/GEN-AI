import {
  Box,
  Chip,
  List,
  Paper,
  Typography
} from '@mui/material';
import React from 'react';
import { PublicTodo, Todo } from '../../types';
import { TodoItem } from './TodoItem';

interface TodoListProps {
  todos: (Todo | PublicTodo)[];
  onToggle?: (id: number, completed: boolean) => void;
  onEdit?: (todo: Todo | PublicTodo) => void;
  onDelete?: (id: number) => void;
  readOnly?: boolean;
  emptyMessage?: string;
  title?: string;
}

export const TodoList: React.FC<TodoListProps> = ({
  todos,
  onToggle,
  onEdit,
  onDelete,
  readOnly = false,
  emptyMessage = 'No todos found',
  title,
}) => {
  const completedCount = todos.filter(todo => todo.completed).length;
  const totalCount = todos.length;

  if (todos.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          {emptyMessage}
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {title && (
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6">{title}</Typography>
          <Chip
            label={`${completedCount}/${totalCount} completed`}
            size="small"
            color={completedCount === totalCount ? 'success' : 'default'}
          />
        </Box>
      )}
      
      <List sx={{ p: 0 }}>
        {todos.map((todo) => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={onToggle}
            onEdit={onEdit}
            onDelete={onDelete}
            readOnly={readOnly}
          />
        ))}
      </List>
    </Box>
  );
};