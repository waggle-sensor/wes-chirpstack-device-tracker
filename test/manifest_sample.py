class ManifestTemplate:
    def __init__(self):
        self.sample = {
            "vsn": "W001",
            "name": "000077A12S23AD1A",
            "phase": "Deployed",
            "project": "SAMPLE",
            "address": "OVER, HERE, TX",
            "gps_lat": 31.602896,
            "gps_lon": 11.001716,
            "modem": None,
            "tags": [],
            "computes": [
                {
                    "name": "nxcore",
                    "serial_no": "57A16A22CA9D",
                    "zone": "core",
                    "hardware": {
                        "hardware": "xaviernx",
                        "hw_model": "xavierNX",
                        "hw_version": "NGX003",
                        "sw_version": "",
                        "manufacturer": "ConnectTech",
                        "datasheet": "https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-xavier-nx/",
                        "capabilities": [
                            "gpu",
                            "cuda102",
                            "arm64"
                        ],
                        "description": "",
                        "cpu": "6000",
                        "cpu_ram": "8092",
                        "gpu_ram": "8092",
                        "shared_ram": True
                    }
                },
                {
                    "name": "rpi",
                    "serial_no": "E71E026AABB1",
                    "zone": "shield",
                    "hardware": {
                        "hardware": "rpi-4gb",
                        "hw_model": "RPI4B",
                        "hw_version": "rpi4b-4g",
                        "sw_version": "",
                        "manufacturer": "Raspberry Pi",
                        "datasheet": "https://www.raspberrypi.com/products/raspberry-pi-4-model-b/",
                        "capabilities": [
                            "arm64",
                            "poe"
                        ],
                        "description": "",
                        "cpu": "4000",
                        "cpu_ram": "4096",
                        "gpu_ram": "",
                        "shared_ram": True
                    }
                }
            ],
            "sensors": [
                {
                    "name": "top_camera",
                    "scope": "global",
                    "labels": [],
                    "serial_no": "",
                    "uri": "",
                    "hardware": {
                        "hardware": "fe-8010",
                        "hw_model": "XNF-8010RV",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "Hanwha Techwin",
                        "datasheet": "https://www.hanwhasecurity.com/media/attachment/file/d/a/datasheet_xnf-8010r_xnf-8010rv_xnf-8010rvm_180918.pdf",
                        "capabilities": [
                            "camera"
                        ],
                        "description": "# 6 MP 360˚ Outdoor Fisheye Camera\r\n\r\nWisenet X powered by Wisenet 5 network outdoor vandal fisheye, 6 MP CMOS sensor, 2048x2048 @ 30fps with WDR off/on(120dB), 1.6mm fixed lens (192°), H.265/H.264/MJPEG, WiseStream II compression technology, USB port for easy installation, advanced video/audio and business analytics, simple focus, dual SD card slots, HLC, Defog detection, DIS , 12VDC/PoE, IP66, IK10\r\n\r\nKey features:\r\n\r\n- 2048 x 2048 resolution, 30fps\r\n- Fisheye lens 1.6mm (192°X192°) W/ simple focus\r\n- Built-in IR for up to 49' or 15m\r\n- Triple Codec: H.265, H.264 and MJPEG multiple streaming\r\n- WiseStream II compression technology\r\n- WDR 120dB @30fps\r\n- Loitering, directional detection, fog detection, tampering, Motion detection, object enter or exit an area\r\n- Sound Classification, heatmap, people counting and queue line management\r\n- Dual SD cards slots\r\n- Power: PoE or 12VDC\r\n- IP66 / IK10"
                    }
                },
                {
                    "name": "bottom_camera",
                    "scope": "global",
                    "labels": [],
                    "serial_no": "",
                    "uri": "",
                    "hardware": {
                        "hardware": "ptz-8081",
                        "hw_model": "XNV-8081Z",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "Hanwha Techwin",
                        "datasheet": "https://www.hanwhasecurity.com/media/attachment/file/d/a/datasheet_xnv-6081z_xnv-8081z_190218.pdf",
                        "capabilities": [
                            "camera"
                        ],
                        "description": "# 5MP Dome PTRZ Camera\r\n\r\nThe Wisenet X series PLUS powered by Wisenet 5 network outdoor vandal dome camera features a modular structure, 5MP @ 30fps, motorized vari-focal lens 2.6x (3.6 ~ 9.4mm) (102.5° ~ 38.7°), and PTRZ capability for easy installation. Triple codec H.265/H.264/MJPEG with WiseStream II technology reduces bandwidth and storage requirements. Additional features include 120dB WDR, USB port for easy installation, advanced video analytics, sound classification and business analytics, shock detection, audio playback, true D/N, dual SD card, hallway view, HLC, fog detection, DIS (Gyro), 12VDC/PoE, optional 24VAC, IP67/IP66/IP6K9K, IK10+, NEMA 4X, -50°C ~ +60°C (-58°F ~ +140°F), white color, ivory skin included, optional black skin cover. The modular design allows for easy installation of the camera case separately from the camera module. In addition, the camera module box includes a cutout for easy configuration without disassembling the camera/case.\r\n\r\nKey features:\r\n\r\n- 5 megapixel resolution\r\n- 2.6x (3.6 ~ 9.4mm) motorized varifocal lens with PTRZ\r\n- 30fps@all resolutions (H.265/H.264)\r\n- H.265, H.264, MJPEG codec supported, multiple streaming\r\n- Day & Night (ICR), WDR (120dB), Defog\r\n- Shock detection, Loitering, Directional detection, Fog detection, Audio detection, Digital auto tracking, Sound classification, Tampering\r\n- Motion detection, Handover, Audio event playback\r\n- Dual SD/SDHC/SDXC memory slots (Max. 512GB)\r\n- Hallway view, WiseStream II support, IP67/IP66/IP6K9K, IK10+, NEMA 4X\r\n- LDC support (Lens Distortion Correction)\r\n- PoE / 12V DC, Bi-directional audio support\r\n- White camera with ivory skin included\r\n- Weathercap included"
                    }
                },
                {
                    "name": "bme280",
                    "scope": "nxcore",
                    "labels": [],
                    "serial_no": "",
                    "uri": "",
                    "hardware": {
                        "hardware": "bme280",
                        "hw_model": "BME280",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "Bosch",
                        "datasheet": "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf",
                        "capabilities": [],
                        "description": "# Relative Humidity, Barometric Pressure, and Temperature Sensor\r\n\r\nThe BME280 is a humidity sensor especially developed for mobile applications and wearables where size and low power consumption are key design parameters. The unit combines high linearity and high accuracy sensors and is perfectly feasible for low current consumption, long-term stability and high EMC robustness. The humidity sensor offers an extremely fast response time and therefore supports performance requirements for emerging applications such as context awareness, and high accuracy over a wide temperature range."
                    }
                },
                {
                    "name": "gps",
                    "scope": "nxcore",
                    "labels": [],
                    "serial_no": "",
                    "uri": "",
                    "hardware": {
                        "hardware": "gps",
                        "hw_model": "VK-162",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "Geekstory",
                        "datasheet": "https://wifire-data.sdsc.edu/dataset/db766c1a-5895-4e0f-b395-db5715818043/resource/687ae0a8-60ce-4af0-a2a8-cc794652ce72/download/vk2828u7g5lf-data-sheet-20150902.pdf",
                        "capabilities": [],
                        "description": "# USB GPS Receiver\r\n\r\nThe VK-162 GPS Receiver is a low cost High sensitivity GPS Receiver + Internal Antenna with USB connector. It is a stand alone GPS receiver providing a solution with high position and speed accuracy performances as well as high sensitivity and tracking capabilities in urban conditions."
                    }
                },
                {
                    "name": "lorawan",
                    "scope": "nxcore",
                    "labels": [],
                    "serial_no": "",
                    "uri": "",
                    "hardware": {
                        "hardware": "lorawan",
                        "hw_model": "LoRaWAN Gateway",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "RAK",
                        "datasheet": "https://docs.rakwireless.com/Product-Categories/WisLink/RAK2287/Datasheet/",
                        "capabilities": [
                            "lorawan"
                        ],
                        "description": "# LPWAN Concentrator Module / LoRaWAN Gateway \r\n\r\nThe *RAK2287* is an LPWAN Concentrator Module with mini-PCIe form factor based on Semtech SX1302, which enables an easy integration into an existing router or other network equipment with LPWAN Gateway capabilities. It can be used in any embedded platform offering a free mini-PCIe slot with SPI connection. Furthermore, *ZOE-M8Q GPS chip* is integrated on board.\r\n\r\nThis module is an exceptional, complete and cost efficient gateway solution offering up to 10 programmable parallel demodulation paths, an 8 x 8 channel LoRa packet detectors, 8 x SF5-SF12 LoRa demodulators and 8 x SF5-SF10 LoRa demodulators. It is capable of detecting uninterrupted combination of packets at 8 different spreading factors and 10 channels with continuous demodulation of up to 16 packets. This product is best for smart metering fixed networks and Internet-of-Things (IoT) applications, that can cover up to 500 nodes per km² in an environment of moderate interference."
                    }
                },
                {
                    "name": "bme680",
                    "scope": "rpi",
                    "labels": [],
                    "serial_no": "",
                    "uri": "",
                    "hardware": {
                        "hardware": "bme680",
                        "hw_model": "BME680",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "Bosch",
                        "datasheet": "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf",
                        "capabilities": [],
                        "description": "# Gas, Relative Humidity, Barometric Pressure, and Temperature Sensor\r\n\r\nThe BME680 is the first gas sensor that integrates high-linearity and high-accuracy gas, pressure, humidity and temperature sensors. It is especially developed for mobile applications and wearables where size and low power consumption are critical requirements. The BME680 guarantees - depending on the specific operating mode - optimized consumption, long-term stability and high EMC robustness. In order to measure air quality for personal wellbeing the gas sensor within the BME680 can detect a broad range of gases such as volatile organic compounds (VOC).\r\n\r\nPossible use cases:\r\n\r\n- Personal air quality tracker\r\n- Air quality mapping\r\n- Air quality inside cars & public transport\r\n- Enhanced context awareness\r\n- Accurate step & calorie tracker\r\n- Quick GPS-fix & improved navigation\r\n- Indicator of too high / low humidity\r\n- Air quality & well-being indicator\r\n- Sleep / recovery tracker\r\n- Weather trend\r\n- Stair counter\r\n- Floor level detection"
                    }
                },
                {
                    "name": "microphone",
                    "scope": "rpi",
                    "labels": [],
                    "serial_no": "",
                    "uri": "",
                    "hardware": {
                        "hardware": "microphone",
                        "hw_model": "ML1-WS IP54",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "ETS",
                        "datasheet": "https://www.etsnm.com/ML1-DOCS/ml1-ws.pdf",
                        "capabilities": [
                            "microphone"
                        ],
                        "description": "# IP54 Rated, Un-Pre-Amplified, Omni-Directional Electret microphone\r\n\r\nThe ML1-WS is a low cost, IP54 rated, un-pre-amplified, omni-directional electret microphone for use with IP cameras accepting microphone level input signals (PC compatible input). The ML1-WS mounts in a standard 1/2 inches electrical knock out hole. The attached cord is 6 feet long and comes standard with a stereo 3.5mm connector on one end. Add -FL to the P/N for a flying lead output for connections to cameras with terminal blocks."
                    }
                },
                {
                    "name": "raingauge",
                    "scope": "rpi",
                    "labels": [],
                    "serial_no": "",
                    "uri": "",
                    "hardware": {
                        "hardware": "raingauge",
                        "hw_model": "RG-15",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "Hydreon",
                        "datasheet": "https://rainsensors.com/wp-content/uploads/sites/3/2020/07/rg-15_instructions_sw_1.000.pdf",
                        "capabilities": [],
                        "description": "# Solid State Rainfall Sensor\r\n\r\nThe Hydreon RG-15 Solid State Tipping Bucket is a rainfall measuring device intended to replace conventional tipping buckets. The RG-15 is rugged, reliable, maintenance-free and features a nominal accuracy of within 10%. The RG-15 is designed to replace tipping bucket rain gauges in many applications where their maintenance requirements make them impractical.\r\n\r\nThe RG-15 uses beams of infrared light within a plastic lens about the size of a tennis ball. The round surface of the lens discourages collection of debris, and the RG-15 has no moving parts to stick, and no water-pathways to clog. The device features an open-collector output that emulates a conventional tipping bucket, as well as serial communications that provide more detailed data and allow for configuration of the device.\r\n\r\nThe RG-15 may be configured through the serial port, or optionally via DIP switches. Power consumption of the RG-15 is very low, and the device is well-suited to solar-power applications.\r\nDip Switches can control the units (inches or millimeters) and resolution (0.01″/0.2mm or 0.001″/0.02mm) of the device. Commands can also be sent via the RS232 serial port to override them."
                    }
                }
            ],
            "resources": [
                {
                    "name": "usbhub",
                    "hardware": {
                        "hardware": "usbhub-10port",
                        "hw_model": "HB30A10AME",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "StarTech.com",
                        "datasheet": "https://www.startech.com/en-us/cards-adapters/hb30a10ame",
                        "capabilities": [],
                        "description": ""
                    }
                },
                {
                    "name": "switch",
                    "hardware": {
                        "hardware": "switch",
                        "hw_model": "ES-8-150W",
                        "hw_version": "",
                        "sw_version": "",
                        "manufacturer": "UniFi",
                        "datasheet": "https://store.ui.com/collections/operator-edgemax-switches/products/edgeswitch-8-150w",
                        "capabilities": [],
                        "description": ""
                    }
                },
                {
                    "name": "wagman",
                    "hardware": {
                        "hardware": "wagman",
                        "hw_model": "wagmanv5",
                        "hw_version": "v5.0",
                        "sw_version": "",
                        "manufacturer": "Surya",
                        "datasheet": "",
                        "capabilities": [],
                        "description": ""
                    }
                },
                {
                    "name": "psu",
                    "hardware": {
                        "hardware": "psu-b0bd",
                        "hw_model": "Efore RCB600",
                        "hw_version": "B0BD",
                        "sw_version": "",
                        "manufacturer": "Enedo",
                        "datasheet": "https://www.trcelectronics.com/efore-roal-modular-power-supply-rcb600",
                        "capabilities": [],
                        "description": ""
                    }
                },
                {
                    "name": "wifi",
                    "hardware": {
                        "hardware": "wifi",
                        "hw_model": "AC650",
                        "hw_version": "V2",
                        "sw_version": "",
                        "manufacturer": "BrosTrend",
                        "datasheet": "",
                        "capabilities": [],
                        "description": ""
                    }
                }
            ],
            "lorawanconnections": [
                {
                    "connection_name": "SFM",
                    "created_at": "2023-12-13T19:47:45.355000Z",
                    "last_seen_at": "2023-12-13T19:47:45.355000Z",
                    "margin": 5,
                    "expected_uplink_interval_sec": 40,
                    "connection_type": "OTAA",
                    "lorawandevice": {
                        "deveui": "7d1f5420e81235c1",
                        "name": "SFM1x Sap Flow",
                        "battery_level": 10,
                        "hardware": {
                            "hardware": "Sap Flow Meter",
                            "hw_model": "SFM1x",
                            "hw_version": "",
                            "sw_version": "",
                            "manufacturer": "ICT International",
                            "datasheet": "https://ictinternational.com/manuals-and-brochures/sfm1x-sap-flow-meter/",
                            "capabilities": [
                                "lorawan"
                            ],
                            "description": "# SFM1x Sap Flow Meter\r\n\r\nThe SFM1x Sap Flow Meter enables individual tree water use and health to be monitored in real time. This is because the SFM has integrated data transmission direct to cloud using IoT/LTE-M Cat-M1. The SFM1x Sap Flow Meter is a discrete standalone instrument based upon the Heat Ratio Method. This measurement principle has proven to be a robust and flexible technique to measure plant water use; being able to measure high, low, zero and reverse flows in a large range of plant anatomies & species from herbaceous to woody, and stem sizes > 10 mm in diameter. The theoretical basis and ratio metric design of the Heat Ratio Method makes possible the measurement of high, low, zero and reverse flows. The SFM1x Sap Flow Meter consists of two temperature sensing needles arranged equidistance above and below a central heater. These needles are inserted into the water conducting tissue of the plant by drilling 3 small parallel holes. Heat is then pulsed every 10 minutes into the water conducting tissue of the plant. The heat is used as a tracer to directly measure the velocity of water movement in the plant stem."
                        }
                    }
                },
                {
                    "connection_name": "test",
                    "created_at": "2023-12-13T19:55:23.676000Z",
                    "last_seen_at": "2023-12-13T19:55:23.676000Z",
                    "margin": 5,
                    "expected_uplink_interval_sec": 30,
                    "connection_type": "OTAA",
                    "lorawandevice": {
                        "deveui": "9821230120031b00",
                        "name": "MFR-Node",
                        "battery_level": 5,
                        "hardware": {
                            "hardware": "Multi-Function Research Node",
                            "hw_model": "MFR-Node-L",
                            "hw_version": "",
                            "sw_version": "",
                            "manufacturer": "ICT International",
                            "datasheet": "https://ictinternational.com/manuals-and-brochures/mfr-node/",
                            "capabilities": [
                                "lorawan"
                            ],
                            "description": "# Multi-Function Research LoRaWAN Node\r\n\r\nThe MFR-NODE has been designed to provide flexible communication, sensor and power options. The MFR-NODE supports SDI-12, four 32-bit dry-contact counting digital inputs and four single-ended (two differential) 0 - 3 V analogue inputs, with selectable 12 V, 5 V or 2.5 V excitation and a 0-100khz frequency input."
                        }
                    }
                }
            ]
        }