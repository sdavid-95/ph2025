# SeeBump - Smart Speed Bump Monitoring System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-ESP32-green.svg)](https://www.espressif.com/en/products/socs/esp32)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg)](https://www.python.org/)

## 📋 Overview

SeeBump is an intelligent IoT-based speed bump monitoring and enforcement system that combines embedded hardware, computer vision, and real-time web analytics to improve road safety and infrastructure maintenance. The system monitors vehicle speeds, detects violations, and tracks structural health degradation of speed bumps in real-time.

### Key Features

- **Real-time Speed Detection**: Computer vision-based vehicle speed monitoring using OpenCV and Haar Cascade classifiers
- **Automated Enforcement**: Alerts and visual warnings triggered for speeding violations
- **Structural Health Monitoring**: Predictive maintenance tracking based on impact severity and frequency
- **Cloud-Connected**: Real-time data synchronization with Supabase backend
- **Web Dashboard**: Next.js-based maintenance application for analytics and monitoring
- **Embedded Control**: ESP32-based hardware controller with Arduino framework integration
- **Scalable Architecture**: Modular design supporting multiple speed bump deployments

---

## 🏗️ System Architecture

The system consists of three main components:

### 1. **Embedded Hardware Controller** (ESP32)
- **Platform**: ESP32 microcontroller
- **Framework**: Arduino/PlatformIO
- **Communication**: Serial UART (115200 baud) for sensor data transmission
- **Sensors**: Integration-ready for accelerometers, distance sensors, and environmental monitoring
- **Location**: `/src/main.cpp`, `/platformio.ini`

### 2. **Computer Vision Engine** (Python)
- **Framework**: OpenCV, dlib
- **Detection**: Haar Cascade-based vehicle detection and tracking
- **Speed Calculation**: Multi-object tracking with velocity estimation
- **Threshold Monitoring**: Configurable speed limit enforcement (default: 35 km/h)
- **Health Algorithm**: Impact-based degradation modeling
- **Location**: `/car-detection/speed_check.py`

### 3. **Maintenance Dashboard** (Next.js Web App)
- **Framework**: Next.js 14+ with TypeScript
- **UI**: React-based responsive interface
- **Backend**: Supabase (PostgreSQL) for real-time data storage
- **Features**: Health status visualization, violation logs, analytics
- **Location**: `/maintenance-app/my-app/`

---

## 📊 Electrical Scheme

<img width="1169" height="827" alt="Schematic_seebump_2025-12-07" src="https://github.com/user-attachments/assets/55c2c79a-bfc6-4a08-abb6-2332350e76a4" />

*Complete electrical schematic showing ESP32 connections, sensor interfaces, and power management circuitry.*

---

## 🚀 Getting Started

### Prerequisites

- **Hardware**: ESP32 development board, sensors (optional for full deployment)
- **Software**: 
  - PlatformIO IDE or Arduino IDE
  - Python 3.8+
  - Node.js 18+ and npm/yarn/pnpm
- **Services**: Supabase account (for cloud features)

### Installation

#### 1. Embedded Firmware Setup

```bash
# Install PlatformIO (if not already installed)
pip install platformio

# Navigate to project root
cd ph2025

# Build and upload to ESP32
pio run --target upload
```

#### 2. Computer Vision Module Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Supabase credentials and SPEED_BUMP_ID

# Run the speed detection system
python car-detection/speed_check.py
```

**Required Environment Variables**:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SPEED_BUMP_ID=your_speed_bump_uuid
```

#### 3. Web Dashboard Setup

```bash
# Navigate to the web app directory
cd maintenance-app/my-app

# Install dependencies
npm install
# or
yarn install

# Run development server
npm run dev
# or
yarn dev

# Access dashboard at http://localhost:3000
```

---

## 📁 Project Structure

```
ph2025/
├── src/
│   └── main.cpp                  # ESP32 firmware (Arduino framework)
├── include/                      # Header files for embedded code
├── lib/                          # Custom libraries for ESP32
├── car-detection/
│   ├── speed_check.py           # Main speed detection script
│   └── myhaar.xml               # Haar Cascade classifier
├── maintenance-app/
│   └── my-app/                  # Next.js maintenance dashboard
│       ├── app/                 # Next.js app directory
│       ├── components/          # React components
│       └── public/              # Static assets
├── platformio.ini               # PlatformIO configuration
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── Embedded_VoltageX.pptx      # Project presentation
```

---

## 🔧 Configuration

### Speed Limit Threshold
Adjust in `car-detection/speed_check.py`:
```python
SPEED_LIMIT_KMH = 35  # Speed limit in km/h
```

### Health Monitoring Parameters
Modify health thresholds in `speed_check.py`:
```python
def get_status_from_health(health: int) -> str:
    if health >= 7000:
        return 'Good'      # 70-100% health
    elif health >= 3000:
        return 'Damaged'   # 30-70% health
    else:
        return 'Critical'  # 0-30% health
```

### Arduino Communication
Configure serial port in `speed_check.py`:
```python
ARDUINO_PORT = "COM3"  # Change to your port (e.g., /dev/ttyUSB0 on Linux)
ARDUINO_BAUDRATE = 115200
```

---

## 📡 API Integration

The system uses Supabase for real-time data synchronization. The database schema includes:

**`speed_bumps` Table**:
- `id` (UUID): Unique speed bump identifier
- `health` (INTEGER): Current health status (0-10000)
- `status` (TEXT): Current status (Good/Damaged/Critical)
- `updated_at` (TIMESTAMP): Last update timestamp

Health updates are triggered when vehicles pass a configured checkpoint and exceed speed limits.

---

## 🎯 Use Cases

1. **Municipal Traffic Management**: Monitor high-traffic areas and enforce speed limits
2. **School Zones**: Enhanced safety monitoring with automated alerts
3. **Predictive Maintenance**: Schedule repairs before critical failures
4. **Traffic Analytics**: Gather data on vehicle speeds and compliance rates
5. **Smart City Integration**: Part of broader IoT infrastructure deployments

---

## 🛠️ Development

### Testing

- **Embedded**: Use PlatformIO's built-in test framework (`/test` directory)
- **Python**: Configure test video source in `speed_check.py`:
  ```python
  video = cv2.VideoCapture('car3.mp4')  # Test video
  # video = cv2.VideoCapture(0)         # Live webcam
  ```
- **Web App**: Next.js built-in testing (configure as needed)

### Debugging

Enable verbose logging in `speed_check.py` by uncommenting debug print statements or adjusting log levels.

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **sdavid-95** - *Project Lead* - [GitHub](https://github.com/sdavid-95)

---

## 🙏 Acknowledgments

- OpenCV community for computer vision libraries
- PlatformIO for embedded development framework
- Supabase for real-time backend infrastructure
- Next.js team for modern web framework

---

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/sdavid-95/ph2025/issues)
- Contact: [Project Discussions](https://github.com/sdavid-95/ph2025/discussions)

---

**Built with ❤️ for safer roads and smarter infrastructure**