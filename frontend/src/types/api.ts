export type ApiResponse<T> = {
  data: T | null;
  message: string;
  request_id?: string;
  errors?: Array<Record<string, unknown>>;
};

export type UserRole = "admin" | "recruiter" | "candidate";
