import React from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';

type CustomButtonProps = {
  title: string;
  onPress: () => void;
};

export const CustomButton = ({ title, onPress }: CustomButtonProps) => (
  <Button title={title} onPress={onPress} />
);

type HeaderProps = {
  title: string;
};

export const Header = ({ title }: HeaderProps) => (
  <View style={styles.header}>
    <Text style={styles.headerText}>{title}</Text>
  </View>
);

const styles = StyleSheet.create({
  header: {
    padding: 20,
    backgroundColor: '#f8f8f8',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
});