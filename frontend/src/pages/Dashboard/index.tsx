import { Grid, Card, Text, Group, RingProgress, SimpleGrid } from '@mantine/core';
import { IconRoute2, IconAirConditioning, IconCloudFog, IconTrees } from '@tabler/icons-react';

export default function Dashboard() {
  const stats = [
    {
      title: 'Routes Optimized',
      value: '156',
      icon: IconRoute2,
      color: 'blue',
      progress: 78,
    },
    {
      title: 'Air Quality Index',
      value: 'Good',
      icon: IconAirConditioning,
      color: 'green',
      progress: 85,
    },
    {
      title: 'Weather Conditions',
      value: 'Clear',
      icon: IconCloudFog,
      color: 'cyan',
      progress: 92,
    },
    {
      title: 'Green Zones',
      value: '24',
      icon: IconTrees,
      color: 'teal',
      progress: 65,
    },
  ];

  return (
    <>
      <Text size="xl" fw={700} mb="lg">
        Dashboard Overview
      </Text>

      <SimpleGrid cols={4} breakpoints={[
        { maxWidth: 'md', cols: 2 },
        { maxWidth: 'xs', cols: 1 },
      ]}>
        {stats.map((stat) => (
          <Card key={stat.title} padding="lg" radius="md" withBorder>
            <Group justify="space-between">
              <stat.icon size={32} color={`var(--mantine-color-${stat.color}-6)`} />
              <RingProgress
                size={80}
                roundCaps
                thickness={8}
                sections={[{ value: stat.progress, color: stat.color }]}
                label={
                  <Text c={stat.color} fw={700} ta="center" size="lg">
                    {stat.progress}%
                  </Text>
                }
              />
            </Group>

            <Group justify="space-between" mt="md">
              <Text size="sm" c="dimmed">
                {stat.title}
              </Text>
              <Text fw={700} size="xl">
                {stat.value}
              </Text>
            </Group>
          </Card>
        ))}
      </SimpleGrid>

      <Grid mt="xl">
        <Grid.Col span={12}>
          <Card padding="lg" radius="md" withBorder>
            <Text size="lg" fw={700} mb="md">
              Recent Routes
            </Text>
            {/* Add a table or list of recent routes here */}
          </Card>
        </Grid.Col>
      </Grid>
    </>
  );
}