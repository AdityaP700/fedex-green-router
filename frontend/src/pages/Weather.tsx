import { Grid, Card, TextInput, Button, Group, Text, Stack, SimpleGrid } from '@mantine/core';
import { IconSun, IconCloud, IconCloudRain, IconTemperature, IconWind, IconDroplet } from '@tabler/icons-react';
import { useState } from 'react';

interface WeatherData {
  location: string;
  current: {
    temp: number;
    humidity: number;
    windSpeed: number;
    condition: string;
    icon: string;
  };
  forecast: Array<{
    date: string;
    temp: number;
    condition: string;
  }>;
}

export default function Weather() {
  const [location, setLocation] = useState('');
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);

  const handleCheckWeather = async () => {
    // TODO: Implement API call to /weather/{location}
    // For now, using mock data
    setWeatherData({
      location: location,
      current: {
        temp: 28,
        humidity: 65,
        windSpeed: 12,
        condition: 'Partly Cloudy',
        icon: 'cloud',
      },
      forecast: [
        { date: '2024-02-20', temp: 27, condition: 'Sunny' },
        { date: '2024-02-21', temp: 29, condition: 'Cloudy' },
        { date: '2024-02-22', temp: 26, condition: 'Rain' },
        { date: '2024-02-23', temp: 28, condition: 'Partly Cloudy' },
      ],
    });
  };

  const getWeatherIcon = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'sunny':
        return <IconSun size={48} />;
      case 'cloudy':
        return <IconCloud size={48} />;
      case 'rain':
        return <IconCloudRain size={48} />;
      default:
        return <IconCloud size={48} />;
    }
  };

  return (
    <Grid>
      <Grid.Col span={12}>
        <Card p="lg" radius="md" withBorder mb="lg">
          <form onSubmit={(e) => {
            e.preventDefault();
            handleCheckWeather();
          }}>
            <Group>
              <TextInput
                label="Location"
                placeholder="Enter city name"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
                style={{ flex: 1 }}
              />
              <Button type="submit" color="cyan" mt={24}>
                Check Weather
              </Button>
            </Group>
          </form>
        </Card>
      </Grid.Col>

      {weatherData && (
        <>
          <Grid.Col span={4}>
            <Card p="lg" radius="md" withBorder>
              <Stack align="center" spacing="xs">  {/* Corrected spacing */}
                {getWeatherIcon(weatherData.current.condition)}
                <Text size="xl">
                  Current Weather
                </Text>
                <Text size="sm" color="dimmed">
                  {weatherData.location}
                </Text>
                <Group spacing="xl" mt="md">
                  <Stack align="center" spacing={0}> {/* Corrected spacing */}
                    <IconTemperature size={24} />
                    <Text size="xl">
                      {weatherData.current.temp}°C
                    </Text>
                    <Text size="xs" color="dimmed">
                      Temperature
                    </Text>
                  </Stack>
                  <Stack align="center" spacing={0}> {/* Corrected spacing */}
                    <IconDroplet size={24} />
                    <Text size="xl">
                      {weatherData.current.humidity}%
                    </Text>
                    <Text size="xs" color="dimmed">
                      Humidity
                    </Text>
                  </Stack>
                  <Stack align="center" spacing={0}> {/* Corrected spacing */}
                    <IconWind size={24} />
                    <Text size="xl">
                      {weatherData.current.windSpeed}km/h
                    </Text>
                    <Text size="xs" color="dimmed">
                      Wind Speed
                    </Text>
                  </Stack>
                </Group>
              </Stack>
            </Card>
          </Grid.Col>

          <Grid.Col span={8}>
            <Card p="lg" radius="md" withBorder>
              <Text size="lg" mb="md">
                4-Day Forecast
              </Text>
              <SimpleGrid cols={4}>
                {weatherData.forecast.map((day) => (
                  <Card key={day.date} p="sm" radius="md" withBorder>
                    <Stack align="center" spacing="xs"> {/* Corrected spacing */}
                      {getWeatherIcon(day.condition)}
                      <Text size="sm">
                        {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                      </Text>
                      <Text size="lg">
                        {day.temp}°C
                      </Text>
                      <Text size="xs" color="dimmed">
                        {day.condition}
                      </Text>
                    </Stack>
                  </Card>
                ))}
              </SimpleGrid>
            </Card>
          </Grid.Col>
        </>
      )}
    </Grid>
  );
}