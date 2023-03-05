import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TextInput, ActivityIndicator, Alert, TouchableOpacity } from 'react-native';
import {Picker} from '@react-native-picker/picker';
import { GooglePlacesAutocomplete } from 'react-native-google-places-autocomplete';
import axios from 'axios'


export default function App() {
  const [destinations, setDestinations] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState('');
  const [time, setTime] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://172.30.7.33:8123/foodbanks');
        setDestinations(response.data);
    
      } catch (error) {
        Alert.alert('Error', error.message);
      }
    };
  
    fetchData();
  }, []);

  const handlePress = async () => {
    setErrorMsg(null)
    if(time && phoneNumber){
      setIsLoading(true);
      try {800
        const response = await fetch(`http://172.30.7.33:8123/driver-pickup`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            destination: selectedDestination,
            time: time,
            phone: phoneNumber,
          }),
        });

        if (!response.ok) {
          throw new Error('Something went wrong');
        }

        Alert.alert('Success', 'Your booking has been confirmed');
        setErrorMsg(null)
      } catch (error) {
        Alert.alert('Error', error.message);
      } finally {
        setIsLoading(false);
      }
    }
    else{
      if(!phoneNumber)
        setErrorMsg("Please select a valid phone number")
      if(!time)
        setErrorMsg("Please select the time you would be available for!")
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Help get food to food banks!</Text>

      <Text style={[styles.label,{marginBottom: -10}]}>Destination:</Text>
	  <View style={styles.pickerContainer}>
		<Picker
			style={styles.picker}
			selectedValue={selectedDestination}
			onValueChange={itemValue => setSelectedDestination(itemValue)}
      itemStyle={styles.pickerItem}
		>
			{destinations.map(destination => (
			<Picker.Item key={destination['name']} label={destination['text']} value={destination['name']}/>
			))}
		</Picker>
	</View>
      <Text style={styles.label}>Time:</Text>
      <TextInput
        style={styles.input}
        value={time}
        onChangeText={setTime}
        placeholder="Select how many minutes you'd like to spend"
        keyboardType="number-pad"
        returnKeyType='done'
      />

      <Text style={styles.label}>Phone Number:</Text>
      <TextInput
        style={styles.input}
        value={phoneNumber}
        onChangeText={setPhoneNumber}
        placeholder="Enter your phone number"
        returnKeyType='done'
        keyboardType="phone-pad"
      />
        {/* <GooglePlacesAutocomplete
            placeholder='Enter Location'
            minLength={2}
            autoFocus={false}
            returnKeyType={'default'}
            fetchDetails={true}
            query={{
                key: 'AIzaSyBgmsz2SeLd9Dea7duWqRp6USYwa3FhzI8',
                language: 'en',
            }}
            styles={styles.mapsSearch}
        /> */}
      {errorMsg ? <Text style={styles.error}>{errorMsg}</Text> : null}
      <TouchableOpacity
        onPress={handlePress}
        style={styles.button}
      >
        {isLoading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Book now</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    width: '90%',
    padding: 20
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    margin: 5,
    marginBottom: 30,
    color: '#333'
    
  },
  button: {
    backgroundColor: '#ebebff',
    width: '40%',
    padding: 15,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
    borderColor: '#d4d4d4',
    borderWidth: 1
  },
  picker: {
    width: 350,
  },
  buttonText: {
    fontWeight: 'bold',
    fontSize: 15,
  },
  pickerItem: {
    fontSize: 14,
  },
  label: {
    fontSize: 18,
    marginBottom: 10,
    alignSelf: 'flex-start',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    padding: 10,
    marginBottom: 20,
    width: '100%',
  },
  mapsSearch: {
    textInputContainer: {
      width: '100%'
    },
    textInput: {
      height: 38,
      color: '#5d5d5d',
      fontSize: 16,
      width: '100%'
    },
    predefinedPlacesDescription: {
      color: '#1faadb',
    }
  },
  error: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 15
  }
});
