import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Alert,
  Fab,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import { Add } from '@mui/icons-material';
import { TodoList } from '../components/todos/TodoList';
import { TodoForm } from '../components/todos/TodoForm';
import { Loading } from '../components/common/Loading';
import { ErrorAlert } from '../components/common/ErrorAlert';
import {
  usePrivateTodos,
  useCreatePrivateTodo,
  useUpdatePrivateTodo,
  useDeletePrivateTodo,
} from '../hooks/useTodos';
import { Todo, CreateTodoDto, UpdateTodoDto } from '../types';
import { getErrorMessage } from '../utils/errorHandler';
import { useAuth } from '../contexts/AuthContext';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`todo-tabpanel-${index}`}
      aria-labelledby={`todo-tab-${index}`}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

export const PrivateTodos: React.FC = () => {
  const { user } = useAuth();
  const [formOpen, setFormOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);

  const { data: todos = [], isLoading, error: fetchError } = usePrivateTodos();
  const createMutation = useCreatePrivateTodo();
  const updateMutation = useUpdatePrivateTodo();
  const deleteMutation = useDeletePrivateTodo();

  const activeTodos = todos.filter(todo => !todo.completed);
  const completedTodos = todos.filter(todo => todo.completed);

  const handleCreate = async (data: CreateTodoDto) => {
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

  const handleEdit = (todo: Todo) => {
    setEditingTodo(todo);
  };

  if (isLoading) {
    return <Loading message="Loading your todos..." />;
  }

  if (fetchError) {
    return <ErrorAlert error={fetchError} />;
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          My Todos
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Welcome back, {user?.username}! Manage your private todos here.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Paper sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={tabValue}
            onChange={(_, newValue) => setTabValue(newValue)}
            aria-label="todo tabs"
          >
            <Tab label={`Active (${activeTodos.length})`} />
            <Tab label={`Completed (${completedTodos.length})`} />
          </Tabs>
        </Paper>

        <TabPanel value={tabValue} index={0}>
          <TodoList
            todos={activeTodos}
            onToggle={handleToggle}
            onEdit={handleEdit}
            onDelete={handleDelete}
            emptyMessage="No active todos. Create one to get started!"
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <TodoList
            todos={completedTodos}
            onToggle={handleToggle}
            onEdit={handleEdit}
            onDelete={handleDelete}
            emptyMessage="No completed todos yet."
          />
        </TabPanel>
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
        isPublic={false}
        showPublicToggle={true}
      />
    </Container>
  );
};