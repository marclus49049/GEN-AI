export interface Todo {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  is_public: boolean;
  user_id?: number;
  created_at: string;
  updated_at?: string;
}

export interface CreateTodoDto {
  title: string;
  description?: string;
  is_public?: boolean;
}

export interface UpdateTodoDto {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface PublicTodo {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  is_public: boolean; // Always true for public todos
  created_at: string;
  user_id?: number;
  owner?: string; // username of the owner
}

export interface PublicTodoDto {
  title: string;
  description?: string;
}