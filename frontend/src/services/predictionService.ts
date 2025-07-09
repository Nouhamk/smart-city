import { apiClient } from './api.service';

class PredictionService {
  async getPredictions() {
    return await apiClient.get('/api/prediction/');
  }

  async getPredictionById(id: string) {
    return await apiClient.get(`/api/prediction/${id}/`);
  }

  async getPredictionsByRegion(region: string) {
    return await apiClient.get(`/api/prediction/?region=${region}`);
  }

  async getPredictionsByDate(date: string) {
    return await apiClient.get(`/api/prediction/?date=${date}`);
  }
}

export default new PredictionService(); 