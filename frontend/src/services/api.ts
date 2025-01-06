import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const routeApi = {
    optimize: async (origin: string, destination: string, vehicleType: string) => {
        const response = await api.post('/routes/optimize', {
            origin,
            destination,
            vehicle_type: vehicleType,
        });
        return response.data;
    },
};

export const vehicleApi = {
    getTypes: async () => {
        const response = await api.get('/vehicles/types');
        return response.data;
    },
    estimateEmissions: async (params: {
        vehicle_type: string;
        distance: number;
        cargo_weight: number;
    }) => {
        const response = await api.post('/vehicles/estimate-emissions', params);
        return response.data;
    },
};

export const metricsApi = {
    getEnvironmentalImpact: async () => {
        const response = await api.get('/metrics/environmental-impact');
        return response.data;
    },
    getTrafficPatterns: async () => {
        const response = await api.get('/metrics/traffic-patterns');
        return response.data;
    },
};

export default api; 