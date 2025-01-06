import { Grid, Card, TextInput, Button, Group, Select } from '@mantine/core';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useState, ChangeEvent } from 'react';

interface VehicleOption {
  value: string;
  label: string;
}

export default function RouteOptimizer() {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [vehicleType, setVehicleType] = useState('');

  const handleOptimizeRoute = () => {
    // TODO: Implement API call to /route/optimize
    console.log('Optimizing route:', { origin, destination, vehicleType });
  };

  const vehicleOptions: VehicleOption[] = [
    { value: 'electric', label: 'Electric Vehicle' },
    { value: 'hybrid', label: 'Hybrid Vehicle' },
    { value: 'diesel', label: 'Diesel Vehicle' },
  ];

  return (
    <Grid>
      <Grid.Col span={4}>
        <Card p="lg" radius="md" withBorder>
          <form onSubmit={(e: React.FormEvent) => {
            e.preventDefault();
            handleOptimizeRoute();
          }}>
            <TextInput
              label="Origin"
              placeholder="Enter starting point"
              value={origin}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setOrigin(e.target.value)}
              required
              mb="md"
            />

            <TextInput
              label="Destination"
              placeholder="Enter destination"
              value={destination}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setDestination(e.target.value)}
              required
              mb="md"
            />

            <Select
              label="Vehicle Type"
              placeholder="Select vehicle type"
              value={vehicleType}
              onChange={(value: string | null) => setVehicleType(value || '')}
              data={vehicleOptions}
              required
              mb="xl"
            />

            <Group justify="flex-end">
              <Button type="submit" color="green">
                Optimize Route
              </Button>
            </Group>
          </form>
        </Card>
      </Grid.Col>

      <Grid.Col span={8}>
        <Card p="lg" radius="md" withBorder style={{ height: '600px' }}>
          <MapContainer
            center={[20.5937, 78.9629]} // Center of India
            zoom={5}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {/* Add markers and route polyline here when available */}
          </MapContainer>
        </Card>
      </Grid.Col>
    </Grid>
  );
} 