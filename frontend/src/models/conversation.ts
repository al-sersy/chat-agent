export interface UserMessage {
  type: "user_message";
  id: string;
  timestamp: string;
  content: string;
}

export interface AssistantMessage {
  type: "assistant_message";
  id: string;
  timestamp: string;
  content: string;
}

export interface ToolCall {
  type: "tool_call";
  id: string;
  timestamp: string;
  tool_call_id: string;
  tool_name: string;
  arguments: Record<string, unknown>;
}

export interface ToolResult {
  type: "tool_result";
  id: string;
  timestamp: string;
  tool_call_id: string;
  content: string;
  truncated: boolean;
}

export interface ErrorItem {
  type: "error";
  id: string;
  timestamp: string;
  detail: string;
}

export type ConversationItem =
  | UserMessage
  | AssistantMessage
  | ToolCall
  | ToolResult
  | ErrorItem;

