export interface ApiError {
  detail: string;
  status?: number;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}