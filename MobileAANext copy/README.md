# MobileAA Next

This project is a React Native application that has been set up to convert Expo components directly to React Native. It includes a structured approach to organizing components, screens, navigation, and types.

## Project Structure

```
MobileAANext
├── src
│   ├── components        # Reusable components
│   ├── screens           # Application screens
│   ├── navigation        # Navigation setup
│   └── types             # TypeScript types and interfaces
├── App.tsx               # Entry point of the application
├── package.json          # Project dependencies and scripts
├── tsconfig.json         # TypeScript configuration
└── README.md             # Project documentation
```

## Getting Started

To get started with the project, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MobileAANext
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the application**:
   ```bash
   npm start
   ```

## Usage

- The `src/components` directory contains reusable components that can be imported into screens or other components.
- The `src/screens/HomeScreen.tsx` serves as the main screen of the application.
- The `src/navigation/AppNavigator.tsx` sets up the navigation structure using React Navigation.
- TypeScript interfaces and types can be found in `src/types/index.ts`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.