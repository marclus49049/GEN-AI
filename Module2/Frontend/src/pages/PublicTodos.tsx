import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Container,
  Alert,
  Fab,
} from '@mui/material';
import { Add } from '@mui/icons-material';
import { TodoList } from '../components/todos/TodoList';
import { TodoForm } from '../components/todos/TodoForm';
import { Loading } from '../components/common/Loading';
import { ErrorAlert } from '../components/common/ErrorAlert';
import {
  usePublicTodos,
  useCreatePublicTodo,
  useUpdatePublicTodo,
  useDeletePublicTodo,
} from '../hooks/useTodos';
import { PublicTodo, PublicTodoDto, UpdateTodoDto } from '../types';
import { getErrorMessage } from '../utils/errorHandler';

export const PublicTodos: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<PublicTodo | null>(null);
  const [error, setError] = useState('');

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
          These todos are visible to everyone. No login required!
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <TodoList
          todos={todos}
          onToggle={handleToggle}
          onEdit={handleEdit}
          onDelete={handleDelete}
          emptyMessage="No public todos yet. Create the first one!"
        />
      </Box>

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