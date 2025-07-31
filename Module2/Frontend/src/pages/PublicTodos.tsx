import { Add } from '@mui/icons-material';
import {
  Alert,
  Box,
  Button,
  Container,
  Fab,
  Paper,
  Typography,
} from '@mui/material';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { Loading } from '../components/common/Loading';
import { TodoForm } from '../components/todos/TodoForm';
import { TodoList } from '../components/todos/TodoList';
import { useAuth } from '../contexts/AuthContext';
import {
  useCreatePublicTodo,
  useDeletePublicTodo,
  usePublicTodos,
  useUpdatePublicTodo,
} from '../hooks/useTodos';
import { PublicTodo, PublicTodoDto, UpdateTodoDto } from '../types';
import { ROUTES } from '../utils/constants';
import { getErrorMessage } from '../utils/errorHandler';

export const PublicTodos: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<PublicTodo | null>(null);
  const [error, setError] = useState('');
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const { data: todos = [], isLoading, error: fetchError } = usePublicTodos();
  const createMutation = useCreatePublicTodo();
  const updateMutation = useUpdatePublicTodo();
  const deleteMutation = useDeletePublicTodo();

  const handleCreate = async (data: PublicTodoDto) => {
    try {
      await createMutation.mutateAsync(data);
      setFormOpen(false);
      setError('');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleUpdate = async (data: UpdateTodoDto) => {
    if (!editingTodo) return;

    try {
      await updateMutation.mutateAsync({ id: editingTodo.id, data });
      setEditingTodo(null);
      setError('');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleToggle = async (id: number, completed: boolean) => {
    try {
      await updateMutation.mutateAsync({ id, data: { completed } });
      setError('');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this todo?')) {
      try {
        await deleteMutation.mutateAsync(id);
        setError('');
      } catch (err) {
        setError(getErrorMessage(err));
      }
    }
  };

  const handleEdit = (todo: PublicTodo) => {
    setEditingTodo(todo);
  };

  if (isLoading) {
    return <Loading message="Loading public todos..." />;
  }

  if (fetchError) {
    return <ErrorAlert error={fetchError} />;
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Public Todos
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          These todos are visible to everyone. Login required to create new todos.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {!isAuthenticated && (
          <Paper sx={{ p: 3, mb: 3, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Want to create a public todo?
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Login to create and manage your own public todos that others can collaborate on.
            </Typography>
            <Button 
              variant="contained" 
              onClick={() => navigate(ROUTES.LOGIN)}
              sx={{ mr: 1 }}
            >
              Login
            </Button>
            <Button 
              variant="outlined" 
              onClick={() => navigate(ROUTES.REGISTER)}
            >
              Register
            </Button>
          </Paper>
        )}

        <TodoList
          todos={todos}
          onToggle={isAuthenticated ? handleToggle : undefined}
          onEdit={isAuthenticated ? handleEdit : undefined}
          onDelete={isAuthenticated ? handleDelete : undefined}
          emptyMessage="No public todos yet. Create the first one!"
        />
      </Box>

      {isAuthenticated && (
        <Fab
          color="primary"
          aria-label="add"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
          }}
          onClick={() => setFormOpen(true)}
        >
          <Add />
        </Fab>
      )}

      <TodoForm
        open={formOpen || !!editingTodo}
        onClose={() => {
          setFormOpen(false);
          setEditingTodo(null);
        }}
        onSubmit={editingTodo ? handleUpdate as any : handleCreate as any}
        todo={editingTodo}
        isPublic={true}
        showPublicToggle={false}
      />
    </Container>
  );
};