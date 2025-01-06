import { Container, Title, SimpleGrid, Card, Text } from '@mantine/core';

export default function Dashboard() {
  const stats = [
    { title: 'Routes Optimized', value: '150+' },
    { title: 'CO2 Saved', value: '2.5 tons' },
    { title: 'Green Zones', value: '25' },
    { title: 'Active Vehicles', value: '45' },
  ];

  return (
    <Container size="lg">
      <Title order={1} mb="xl">Dashboard</Title>
      
      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }}>
        {stats.map((stat) => (
          <Card key={stat.title} padding="lg" radius="md" withBorder>
            <Text size="lg" fw={500} c="dimmed">{stat.title}</Text>
            <Text size="xl" fw={700} mt="sm">{stat.value}</Text>
          </Card>
        ))}
      </SimpleGrid>
    </Container>
  );
} 