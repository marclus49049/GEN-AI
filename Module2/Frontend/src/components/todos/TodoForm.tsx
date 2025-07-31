import {
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  TextField,
} from '@mui/material';
import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { CreateTodoDto, PublicTodo, PublicTodoDto, Todo, UpdateTodoDto } from '../../types';

interface TodoFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CreateTodoDto | UpdateTodoDto | PublicTodoDto) => void;
  todo?: Todo | PublicTodo | null;
  isPublic?: boolean;
  showPublicToggle?: boolean;
}

interface FormData {
  title: string;
  description: string;
  is_public: boolean;
}

export const TodoForm: React.FC<TodoFormProps> = ({
  open,
  onClose,
  onSubmit,
  todo,
  isPublic = false,
  showPublicToggle = true,
}) => {
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<FormData>();

  useEffect(() => {
    if (todo) {
      setValue('title', todo.title);
      setValue('description', todo.description || '');
      setValue('is_public', todo.is_public);
    } else {
      reset({
        title: '',
        description: '',
        is_public: isPublic,
      });
    }
  }, [todo, isPublic, setValue, reset]);

  const handleFormSubmit = (data: FormData) => {
    if (todo) {
      // Update existing todo
      const updateData: UpdateTodoDto = {
        title: data.title,
        description: data.description || undefined,
      };
      onSubmit(updateData);
    } else {
      // Create new todo
      const createData: CreateTodoDto = {
        title: data.title,
        description: data.description || undefined,
        is_public: showPublicToggle ? data.is_public : isPublic,
      };
      onSubmit(createData);
    }
    handleClose();
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <DialogTitle>{todo ? 'Edit Todo' : 'Create New Todo'}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              {...register('title', {
                required: 'Title is required',
                minLength: {
                  value: 1,
                  message: 'Title must not be empty',
                },
              })}
              label="Title"
              fullWidth
              margin="normal"
              error={!!errors.title}
              helperText={errors.title?.message}
              autoFocus
            />

            <TextField
              {...register('description')}
              label="Description (optional)"
              fullWidth
              margin="normal"
              multiline
              rows={3}
            />

            {showPublicToggle && !todo && (
              <FormControlLabel
                control={
                  <Checkbox
                    {...register('is_public')}
                    defaultChecked={isPublic}
                  />
                }
                label="Make this todo public"
                sx={{ mt: 2 }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button type="submit" variant="contained">
            {todo ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};