import { useState, useRef } from 'react'
import { View, Text, StyleSheet , FlatList, TextInput, TouchableOpacity, Alert } from 'react-native'

import React from 'react'
import axios from 'axios'

const ChatBot = () => {
    const [data, setData] = useState([{ type: "bot", text: "Hi, if you'd like to save the planet bite-by-bite, please let me know details about the food you'd like to donate!" }]);
    const api_url = 'http://172.30.7.33:8123/chat'
    const [textInput, setTextInput] = useState('');
    const [id, setId] = useState(-1);
    const flatList = useRef(null);

    if(id === -1)
        setId(Math.floor(Math.random() * 10000) + 1)
    const handleSend = async () => {
        const newData = [...data, { type: "user", text: textInput }];
        setData(newData);
        setTextInput("");
        
        try {
          const response = await axios.post(
            api_url,
            {
              query: textInput,
              id: id,
            },
            {
              headers: {
                "Content-Type": "application/json",
              },
            }
          );
          const text = response.data.prompt;
          const newBotData = [...newData, { type: "bot", text }];
          setData(newBotData);
        } catch (error) {
          console.error(error);
        }
      };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Talk to our AI to save some food!</Text>
       <FlatList
        data={data}
        ref = {flatList}
        keyExtractor={(_, index) => index.toString()}
        style={styles.body}
        onContentSizeChange={()=> {flatList.current.scrollToEnd()}}
        renderItem={({item}) =>(
            <View style={[styles.chatMessage, item.type === 'user'? styles.chatMessageUser : styles.chatMessageBot]}>
                {item.type === 'bot' ? <Text style={[styles.botMessageTitle]}>
                    {'AI: '}
                  </Text> : null}
                <Text style={[styles.message,item.type === 'user'? styles.userMessage : styles.botMessage]}>
                    {item.text}
                </Text>
            </View>
        )}
        />
        <TextInput style={styles.input} value = {textInput}
            onChangeText = {text=>setTextInput(text)}
            placeholder= "Ask me anything!"
        />
        <TouchableOpacity
            style = {styles.button}
            onPress={handleSend}>
            <Text style={styles.buttonText}> Query </Text>
        </TouchableOpacity>
    </View>
  )
}

export default ChatBot

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    width: '100%',
    paddingBottom: 20,
    maxHeight: '100%',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 20,
    padding: 10,
    color: '#333'
    
  },
  chatMessage: {
    flexDirection: 'row',
    paddingTop: 10,
    paddingBottom: 10
  },
  chatMessageUser:{
    alignItems: 'center',
    justifyContent: 'flex-end'
  },
  chatMessageBot:{
    flexDirection: 'row'
  },
  botMessageTitle: {
    color: 'red',
    fontWeight: 'bold',
    paddingTop: 10,
  },
  body: {
    flex: 1,
    backgroundColor: '#f1f1f1',
    width: '90%',
    maxHeight: '100%',
    height: '80%',
    margin: 10,
    borderRadius: 15,
    paddingLeft: 20,
    paddingRight: 20,
    borderWidth: 0.5,
    borderColor: '#696969'
  },
  message:{
    fontSize: 16,
    maxWidth: '70%',
    letterSpacing: 0.45,
    marginLeft: 5,
    padding: 8,
    borderWidth: 1,
    borderRadius: 5,
    borderColor: '#d4d4d4'
  },
  userMessage: {
    textAlign:'right',
  },
  botMessage: {
  },
  input: {
    borderWidth: 1,
    borderRadius: 5,
    width: '90%',
    height: 60,
    marginBottom: 10,
    borderRadius: 10,
    borderColor: '#d4d4d4',
    padding: 10
  },
  button: {
    backgroundColor: '#ebebff',
    width: '30%',
    padding: 15,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
    borderColor: '#d4d4d4',
    borderWidth: 0.5
  },
  buttonText: {
    fontWeight: 'bold',
    fontSize: 15,
  }
});
