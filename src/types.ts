export interface ChatMessage {
  raw_request: string;
  raw_reply: string;
}

export interface TokenUsage {
  prompt_token_count: number;
  candidates_token_count: number;
  total_token_count: number;
  thoughts_token_count?: number;
}

export interface MetricsData {
  total_messages: number;
  total_prompt_tokens: number;
  total_candidate_tokens: number;
  total_tokens: number;
  average_prompt_tokens: number;
  average_candidate_tokens: number;
  average_total_tokens: number;
  average_response_length: number;
  min_total_tokens: number;
  max_total_tokens: number;
  timestamp: string;
}

export interface AppState {
  messages: ChatMessage[];
  metrics: MetricsData | null;
  currentMenu: 'import' | 'metrics';
}
