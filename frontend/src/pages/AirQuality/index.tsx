import { Grid, Card, TextInput, Button, Group, RingProgress, Text, Stack } from '@mantine/core';
import { IconWind } from '@tabler/icons-react';
import { useState } from 'react';

interface AirQualityData {
  aqi: number;
  location: string;
  pollutants: {
    pm25: number;
    pm10: number;
    no2: number;
    so2: number;
    o3: number;
    co: number;
  };
}

export default function AirQuality() {
  const [location, setLocation] = useState('');
  const [airQualityData, setAirQualityData] = useState<AirQualityData | null>(null);

  const handleCheckAirQuality = async () => {
    setAirQualityData({
      aqi: 75,
      location: location,
      pollutants: {
        pm25: 15.2,
        pm10: 45.8,
        no2: 21.3,
        so2: 8.4,
        o3: 52.1,
        co: 0.8,
      },
    });
  };

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return 'green';
    if (aqi <= 100) return 'yellow';
    if (aqi <= 150) return 'orange';
    if (aqi <= 200) return 'red';
    return 'purple';
  };

  return (
    <Grid gap="md">
      <Grid.Col span={12}>
        <Card padding="lg" radius="md" withBorder mb="lg">
          <form onSubmit={(e) => {
            e.preventDefault();
            handleCheckAirQuality();
          }}>
            <Group justify="space-between" align="center">
              <TextInput
                label="Location"
                placeholder="Enter city or area name"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
                style={{ flex: 1 }}
              />
              <Button type="submit" color="blue" mt={24}>
                Check Air Quality
              </Button>
            </Group>
          </form>
        </Card>
      </Grid.Col>

      {airQualityData && (
        <>
          <Grid.Col span={4}>
            <Card padding="lg" radius="md" withBorder>
              <Stack align="center" gap="xs">
                <IconWind size={48} color={`var(--mantine-color-${getAQIColor(airQualityData.aqi)}-6)`} />
                <Text size="xl" fw={700} ta="center">
                  Air Quality Index
                </Text>
                <RingProgress
                  size={180}
                  thickness={16}
                  sections={[{ value: (airQualityData.aqi / 500) * 100, color: getAQIColor(airQualityData.aqi) }]}
                  label={
                    <Text size="xl" ta="center" fw={700}>
                      {airQualityData.aqi}
                    </Text>
                  }
                />
                <Text size="sm" c="dimmed" ta="center">
                  {location}
                </Text>
              </Stack>
            </Card>
          </Grid.Col>

          <Grid.Col span={8}>
            <Card padding="lg" radius="md" withBorder>
              <Text size="lg" fw={700} mb="md">
                Pollutant Levels
              </Text>
              <Grid gap="md">
                {Object.entries(airQualityData.pollutants).map(([key, value]) => (
                  <Grid.Col span={4} key={key}>
                    <Card padding="sm" radius="md" withBorder>
                      <Text size="sm" c="dimmed" tt="uppercase" ta="center">
                        {key}
                      </Text>
                      <Text size="lg" fw={700} ta="center">
                        {value} µg/m³
                      </Text>
                    </Card>
                  </Grid.Col>
                ))}
              </Grid>
            </Card>
          </Grid.Col>
        </>
      )}
    </Grid>
  );
}