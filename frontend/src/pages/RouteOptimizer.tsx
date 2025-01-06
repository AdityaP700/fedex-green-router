import { Grid, Card, TextInput, Button, Group, Select, LoadingOverlay } from '@mantine/core';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useState, useEffect } from 'react';
import { routeApi, vehicleApi } from '../services/api';
import { notifications } from '@mantine/notifications';

interface VehicleOption {
  value: string;
  label: string;
}

export default function RouteOptimizer() {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [vehicleType, setVehicleType] = useState('');
  const [vehicleOptions, setVehicleOptions] = useState<VehicleOption[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load vehicle types when component mounts
    const loadVehicleTypes = async () => {
      try {
        const types = await vehicleApi.getTypes();
        setVehicleOptions(
          Object.entries(types).map(([key, value]: [string, any]) => ({
            value: key,
            label: value.name
          }))
        );
      } catch (error) {
        notifications.show({
          title: 'Error',
          message: 'Failed to load vehicle types',
          color: 'red'
        });
      }
    };

    loadVehicleTypes();
  }, []);

  const handleOptimizeRoute = async () => {
    setLoading(true);
    try {
      const result = await routeApi.optimize(origin, destination, vehicleType);
      console.log('Route optimized:', result);
      // TODO: Update map with route
      notifications.show({
        title: 'Success',
        message: 'Route optimized successfully',
        color: 'green'
      });
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to optimize route',
        color: 'red'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Grid gutter="xl" align="flex-start">
      <Grid.Col span={12} breakpoints={{ lg: 4 }}> {/* Corrected responsive behavior */}
        <Card p="lg" radius="md" withBorder pos="relative">
          <LoadingOverlay visible={loading} />
          <form onSubmit={(e: React.FormEvent) => {
            e.preventDefault();
            handleOptimizeRoute();
          }}>
            <TextInput
              label="Origin"
              placeholder="Enter starting point"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              required
              mb="md"
            />

            <TextInput
              label="Destination"
              placeholder="Enter destination"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              required
              mb="md"
            />

            <Select
              label="Vehicle Type"
              placeholder="Select vehicle type"
              value={vehicleType}
              onChange={(value) => setVehicleType(value || '')}
              data={vehicleOptions}
              required
              mb="xl"
            />

            <Group justify="flex-end">
              <Button type="submit" color="green" loading={loading}>
                Optimize Route
              </Button>
            </Group>
          </form>
        </Card>
      </Grid.Col>

      <Grid.Col span={12} breakpoints={{ lg: 8 }}> {/* Corrected responsive behavior */}
        <Card p="lg" radius="md" withBorder style={{ height: '600px', minHeight: '450px' }}>
          <MapContainer
            center={[20.5937, 78.9629]} // Center of India
            zoom={5}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {/* Add markers for origin and destination when coordinates are available */}
          </MapContainer>
        </Card>
      </Grid.Col>
    </Grid>
  );
}