const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = {
  // ========== SQL AGENT ENDPOINTS ==========

  // Generate SQL from natural language
  async generateSQL(question, schema) {
    const response = await fetch(`${API_BASE_URL}/api/v1/sql/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        schema,
        execute: false
      }),
    });
    if (!response.ok) throw new Error("Failed to generate SQL");
    return response.json();
  },

  // Validate SQL query
  async validateSQL(sql, schema) {
    const response = await fetch(`${API_BASE_URL}/api/v1/sql/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sql,
        schema,
        max_rows: 100
      }),
    });
    if (!response.ok) throw new Error("Failed to validate SQL");
    return response.json();
  },

  // Extract schema from uploaded database file
  async extractSchemaFromFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/api/v1/sql/extract-schema`, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to extract schema");
    }
    return response.json();
  },

  // Check SQL agent health
  async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/api/v1/sql/health`);
    if (!response.ok) throw new Error("Failed to check health");
    return response.json();
  },

  // ========== CONVERSATION MANAGEMENT (kept for history) ==========

  async getConversations() {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    if (!response.ok) throw new Error("Failed to fetch conversations");
    return response.json();
  },

  async createConversation(title = "New Chat") {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) throw new Error("Failed to create conversation");
    return response.json();
  },

  async getConversation(conversationId) {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}`,
    );
    if (!response.ok) throw new Error("Failed to fetch conversation");
    return response.json();
  },

  async updateConversation(conversationId, title) {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
      },
    );
    if (!response.ok) throw new Error("Failed to update conversation");
    return response.json();
  },

  async deleteConversation(conversationId) {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}`,
      {
        method: "DELETE",
      },
    );
    if (!response.ok) throw new Error("Failed to delete conversation");
    return response.json();
  },

  async clearConversation(conversationId) {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}/clear`,
      {
        method: "POST",
      },
    );
    if (!response.ok) throw new Error("Failed to clear conversation");
    return response.json();
  },
};
