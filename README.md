# TORCS AI Driver 🚗💨

A deep learning-based autonomous driving model for the TORCS (The Open Racing Car Simulator) environment. This project uses PyTorch to train a neural network that predicts steering, throttle, brake, and gear commands from raw telemetry data.

## 📁 Project Structure

    ProjectRoot/
    ├── Data/                  # Raw telemetry CSV files
    │   └── telemetry_*.csv
    ├── Model/                 # Training script and saved model
    │   ├── model.py
    │   ├── torcs_model.pt
    │   └── scaler.save
    ├── carControl.py
    ├── carState.py
    ├── driver_model.py
    ├── msgParser.py
    ├── pyclient.py
    ├── README.md
    └── .gitignore

## 🧠 Model Overview

- **Input:** Telemetry data including speed, RPM, position, sensor data, etc.
- **Output:** Continuous driving commands – `accel`, `brake`, `steer`, `gear_cmd`
- **Model:** Fully connected neural network using ReLU activations and dropout
- **Loss Function:** SmoothL1Loss
- **Framework:** PyTorch

## 🧪 How to Train

1. Place all CSV telemetry files in the `Data/` folder.
2. Run the training script from the `Model/` directory:

       cd Model
       python model.py

3. The model and scaler will be saved in the `Model/` folder as:
    - `torcs_model.pt`
    - `scaler.save`

## 🛠️ Technologies Used

- Python
- PyTorch
- NumPy, Pandas
- scikit-learn
- TORCS (simulator)

## 📌 Notes

- Be sure to run the training script from inside the `Model/` folder so relative paths work correctly.
- The `.pt` file can later be loaded for inference or used with a driver script in the TORCS environment.

## 📄 License

MIT License

## 🤖 Author

[Asim Iqbal Khan](https://github.com/Asim-Iqbal-Khan)
