import { ChatMessage, MetricsData, TokenUsage } from './types';
import Papa from 'papaparse';
import * as XLSX from 'xlsx';

export function parseJsonSafe(jsonString: string): any {
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    console.error('JSON parse error:', error);
    return null;
  }
}

export function extractTokenUsage(replyJson: any): TokenUsage | null {
  if (typeof replyJson === 'string') {
    replyJson = parseJsonSafe(replyJson);
  }

  if (!replyJson || typeof replyJson !== 'object') {
    return null;
  }

  const tokenUsage = replyJson.token_usage || {};
  
  return {
    prompt_token_count: tokenUsage.prompt_token_count || 0,
    candidates_token_count: tokenUsage.candidates_token_count || 0,
    total_token_count: tokenUsage.total_token_count || 0,
    thoughts_token_count: tokenUsage.thoughts_token_count || 0,
  };
}

export function calculateMetrics(messages: ChatMessage[]): MetricsData {
  if (messages.length === 0) {
    return {
      total_messages: 0,
      total_prompt_tokens: 0,
      total_candidate_tokens: 0,
      total_tokens: 0,
      average_prompt_tokens: 0,
      average_candidate_tokens: 0,
      average_total_tokens: 0,
      average_response_length: 0,
      min_total_tokens: 0,
      max_total_tokens: 0,
      timestamp: new Date().toISOString(),
    };
  }

  let totalPromptTokens = 0;
  let totalCandidateTokens = 0;
  let totalTokens = 0;
  let totalResponseLength = 0;
  let minTokens = Infinity;
  let maxTokens = 0;

  messages.forEach((msg) => {
    const tokenUsage = extractTokenUsage(msg.raw_reply);
    if (tokenUsage) {
      totalPromptTokens += tokenUsage.prompt_token_count;
      totalCandidateTokens += tokenUsage.candidates_token_count;
      totalTokens += tokenUsage.total_token_count;
      
      minTokens = Math.min(minTokens, tokenUsage.total_token_count);
      maxTokens = Math.max(maxTokens, tokenUsage.total_token_count);
    }

    // Try to extract response text length
    const replyJson = parseJsonSafe(msg.raw_reply);
    if (replyJson && typeof replyJson.text === 'string') {
      totalResponseLength += replyJson.text.length;
    }
  });

  const count = messages.length;

  return {
    total_messages: count,
    total_prompt_tokens: totalPromptTokens,
    total_candidate_tokens: totalCandidateTokens,
    total_tokens: totalTokens,
    average_prompt_tokens: Math.round(totalPromptTokens / count),
    average_candidate_tokens: Math.round(totalCandidateTokens / count),
    average_total_tokens: Math.round(totalTokens / count),
    average_response_length: Math.round(totalResponseLength / count),
    min_total_tokens: minTokens === Infinity ? 0 : minTokens,
    max_total_tokens: maxTokens,
    timestamp: new Date().toISOString(),
  };
}

export async function parseCSVFile(file: File): Promise<ChatMessage[]> {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      error: reject,
      complete: (results: any) => {
        const messages: ChatMessage[] = results.data
          .filter((row: any) => row.raw_request && row.raw_reply)
          .map((row: any) => ({
            raw_request: row.raw_request,
            raw_reply: row.raw_reply,
          }));
        resolve(messages);
      },
    });
  });
}

export function parseExcelFile(file: File): Promise<ChatMessage[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      try {
        const workbook = XLSX.read(e.target.result, { type: 'array' });
        const worksheet = workbook.Sheets[workbook.SheetNames[0]];
        const data = XLSX.utils.sheet_to_json(worksheet);
        
        const messages: ChatMessage[] = (data as any[])
          .filter((row: any) => row.raw_request && row.raw_reply)
          .map((row: any) => ({
            raw_request: row.raw_request,
            raw_reply: row.raw_reply,
          }));
        
        resolve(messages);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}

export function parseJsonText(jsonText: string): ChatMessage[] {
  try {
    const data = JSON.parse(jsonText);
    
    if (Array.isArray(data)) {
      return data
        .filter((item: any) => item.raw_request && item.raw_reply)
        .map((item: any) => ({
          raw_request: item.raw_request,
          raw_reply: item.raw_reply,
        }));
    } else if (data.raw_request && data.raw_reply) {
      return [
        {
          raw_request: data.raw_request,
          raw_reply: data.raw_reply,
        },
      ];
    }
    
    return [];
  } catch (error) {
    console.error('JSON text parse error:', error);
    return [];
  }
}

export function exportToCSV(metrics: MetricsData): string {
  const headers = Object.keys(metrics);
  const values = Object.values(metrics).map(v => {
    if (typeof v === 'string') return `"${v}"`;
    return v;
  });

  return [headers.join(','), values.join(',')].join('\n');
}

export function exportToJSON(metrics: MetricsData, messages: ChatMessage[]): string {
  return JSON.stringify(
    {
      metrics,
      summary: {
        export_date: new Date().toISOString(),
        message_count: messages.length,
      },
    },
    null,
    2
  );
}

export function downloadFile(content: string, filename: string, mimeType: string = 'text/plain'): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
