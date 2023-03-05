import { StyleSheet, Text, View, Image, TouchableOpacity } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import ChatBot from './src/chatbot'
import Delivery from './src/deliver';
import Leaderboard from './src/leaderboard'; 

const Stack = createStackNavigator();

function HomeScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Image style={styles.logo} source={require('./logo.png')} />
      <Text style={styles.textTitle}>Welcome to Waste Not!</Text>
      <Text style={styles.text}>40% of all food in the US is wasted every year, resulting in billions of pounds of discarded food. We can help address this by redirecting some of it to people in need.</Text>
      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('Donate')}>
        <Text style={styles.buttonText}>Donate Food</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('Deliver')}>
        <Text style={styles.buttonText}>Deliver Food</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('Leaderboard')}>
        <Text style={styles.buttonText}>Leaderboard</Text>
      </TouchableOpacity>
    </View>
  );
}

function Donate() {
  return (
    <View style={styles.container}>
       <ChatBot/>
    </View>
  );
}

function Deliver() {
  return (
    <View style={styles.container}>
       <Delivery/>
    </View>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Waste Not" component={HomeScreen}/>
        <Stack.Screen name="Donate" component={Donate} />
        <Stack.Screen name="Deliver" component={Deliver} />
        <Stack.Screen name="Leaderboard" component={Leaderboard} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
  },
  logo: {
    width: 200,
    height: 200,
    marginBottom: 20,
  },
  textTitle: {
    fontSize: 20,
    marginBottom: 20,
    fontWeight: 'bold',
  },
  text: {
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center', 
    width: '80%',
  },
  button: {
    backgroundColor: '#3498db',
    width: '35%',
    height: '7%',
    borderRadius: 5,
    padding: 10,
    margin: 10,
    marginBottom: 20,
    alignContent: 'center',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#fff',
    textAlign: 'center',
    fontSize: 17,
  },
});
