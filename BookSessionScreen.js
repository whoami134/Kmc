import React, { useState, useEffect } from 'react';
import { View, Text, Button, TextInput, Picker, StyleSheet } from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BookSessionScreen = ({ navigation }) => {
  const [counselors, setCounselors] = useState([]);
  const [selectedCounselor, setSelectedCounselor] = useState(null);
  const [date, setDate] = useState('');

  useEffect(() => {
    const fetchCounselors = async () => {
      const token = await AsyncStorage.getItem('token');
      const response = await axios.get('https://your-backend-url.com/counselors', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCounselors(response.data);
    };

    fetchCounselors();
  }, []);

  const handleBookSession = async () => {
    const token = await AsyncStorage.getItem('token');
    await axios.post('https://your-backend-url.com/session', {
      counselor_id: selectedCounselor,
      date: date
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    alert('Session booked successfully');
    navigation.navigate('Home');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Book a Session</Text>
      <Picker
        selectedValue={selectedCounselor}
        onValueChange={(itemValue) => setSelectedCounselor(itemValue)}
        style={styles.picker}
      >
        {counselors.map((counselor) => (
          <Picker.Item key={counselor.id} label={counselor.name} value={counselor.id} />
        ))}
      </Picker>
      <TextInput
        style={styles.input}
        placeholder="Date (YYYY-MM-DD)"
        value={date}
        onChangeText={setDate}
      />
      <Button title="Book Session" onPress={handleBookSession} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 16,
  },
  title: {
    fontSize: 24,
    marginBottom: 16,
    textAlign: 'center',
  },
  picker: {
    height: 50,
    width: '100%',
    marginBottom: 12,
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 12,
    paddingHorizontal: 8,
  },
});

export default BookSessionScreen;
