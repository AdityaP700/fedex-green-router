import { Grid, Card, TextInput, Button, Group, Text, Stack, Badge } from '@mantine/core';
import { MapContainer, TileLayer, Circle, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useState } from 'react';
import { IconTree } from '@tabler/icons-react';

interface GreenZone {
  id: string;
  name: string;
  coordinates: [number, number];
  radius: number;
  type: string;
  restrictions: string[];
}

export default function GreenZones() {
  const [city, setCity] = useState('');
  const [zones, setZones] = useState<GreenZone[]>([]);

  const handleSearchZones = async () => {
    // TODO: Implement API call to /green-zones/{city}
    // For now, using mock data
    setZones([
      {
        id: '1',
        name: 'Central Park',
        coordinates: [28.6139, 77.2090],
        radius: 1000,
        type: 'Park',
        restrictions: ['No heavy vehicles', 'Electric vehicles only'],
      },
      {
        id: '2',
        name: 'Green Valley',
        coordinates: [28.6229, 77.2190],
        radius: 800,
        type: 'Residential',
        restrictions: ['Limited delivery hours', 'Noise restrictions'],
      },
    ]);
  };

  const searchFormProps = {
    city,
    setCity,
    handleSearchZones,
  };

  return (
    <Grid>
      <Grid.Col span={12}>
        <Card p="lg" radius="md" withBorder mb="lg">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              searchFormProps.handleSearchZones();
            }}
          >
            <Group>
              <TextInput
                label="City"
                placeholder="Enter city name"
                value={searchFormProps.city}
                onChange={(e) => searchFormProps.setCity(e.target.value)}
                required
                style={{ flex: 1 }}
              />
              <Button type="submit" color="teal" mt={24}>
                Search Green Zones
              </Button>
            </Group>
          </form>
        </Card>
      </Grid.Col>

      <Grid.Col span={8}>
        <Card p="lg" radius="md" withBorder style={{ height: '600px' }}>
          <MapContainer
            center={[28.6139, 77.2090]} // Default to Delhi
            zoom={12}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {zones.map((zone) => (
              <Circle
                key={zone.id}
                center={zone.coordinates}
                radius={zone.radius}
                pathOptions={{ color: 'green', fillColor: 'green', fillOpacity: 0.2 }}
              >
                <Popup>
                  <Text weight={700}>{zone.name}</Text> 
                  <Text size="sm">Type: {zone.type}</Text>
                </Popup>
              </Circle>
            ))}
          </MapContainer>
        </Card>
      </Grid.Col>

      <Grid.Col span={4}>
        <Stack>
          {zones.map((zone) => (
            <Card key={zone.id} p="lg" radius="md" withBorder>
              <Group position="apart" mb="xs">
                <Group>
                  <IconTree size={24} color="green" />
                  <Text weight={700}>{zone.name}</Text> 
                </Group>
                <Badge color="green">{zone.type}</Badge>
              </Group>
              <Text size="sm" color="dimmed" mb="md">
                Radius: {zone.radius}m
              </Text>
              <Text size="sm" weight={500} mb="xs"> 
                Restrictions:
              </Text>
              <Stack spacing="xs"> 
                {zone.restrictions.map((restriction, index) => (
                  <Text key={index} size="sm" color="dimmed">
                    • {restriction}
                  </Text>
                ))}
              </Stack>
            </Card>
          ))}
        </Stack>
      </Grid.Col>
    </Grid>
  );
}