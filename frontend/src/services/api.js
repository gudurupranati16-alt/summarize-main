import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

const handleError = (error, defaultMessage) => {
  if (error.response?.data?.detail) {
    throw new Error(error.response.data.detail);
  }
  throw new Error(error.message || defaultMessage);
};

export const uploadPDF = async (files) => {
  const formData = new FormData();
  if (Array.isArray(files)) {
    files.forEach((file) => {
      formData.append('files', file);
    });
  } else if (files instanceof FileList) {
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });
  } else {
    formData.append('files', files);
  }

  try {
    const response = await api.post('/summarize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to upload PDF');
  }
};

export const getSummaryHistory = async () => {
  try {
    const response = await api.get('/summaries');
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to retrieve summaries');
  }
};

export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.ok;
  } catch {
    return false;
  }
};

export default api;
