import React from 'react';
import { StyleSheet, Text, View, FlatList } from 'react-native';

const leaderboardData = [
  { name: 'John', score: 100 },
  { name: 'Jane', score: 80 },
  { name: 'Bob', score: 70 },
  { name: 'Alice', score: 60 },
  { name: 'Tom', score: 50 },
];

const Leaderboard = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Acknowledge the heroes of our community</Text>
      <FlatList
        data={leaderboardData}
        style={styles.list}
        renderItem={({ item, index }) => (
          <View style={styles.itemContainer}>
            <Text style={styles.itemName}>{index + 1}. {item.name} {index === 0 ? '🏆': (index === 1 ? '🥈': (index === 2 ? '🥉': ''))} </Text>
            <Text style={styles.itemScore}>{item.score} lbs</Text>
          </View>
        )}
        keyExtractor={(item) => item.name}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    width: '100%',
    paddingBottom: 20,
    maxHeight: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    alignContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 20,
    padding: 10,
    color: '#333',
    textAlign: 'center',
    marginBottom: 10
  },
  list: {
    width: '95%',
    backgroundColor: '#f0f0f0',
    maxHeight: 300,
    padding: 20,
    borderRadius: 10,
  },
  itemContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 10,
    marginLeft: '5%',
    marginRight: '5%',
    width: '90%',
    borderRadius: 10,
    marginVertical: 5,
  },
  itemName: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  itemScore: {
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default Leaderboard;
