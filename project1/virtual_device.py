
# MQTT物联网虚拟设备模拟器
# 需要安装: pip install paho-mqtt

import paho.mqtt.client as mqtt
import json
import time
import random
import threading
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VirtualDevice:
    """虚拟设备基类"""
    def __init__(self, device_id, device_type, mqtt_client, publish_interval=5):
        self.device_id = device_id
        self.device_type = device_type
        self.mqtt_client = mqtt_client
        self.publish_interval = publish_interval
        self.is_running = False
        self.thread = None
        
    def generate_data(self):
        """生成设备数据，子类需要重写此方法"""
        raise NotImplementedError
        
    def start(self):
        """启动设备数据发送"""
        self.is_running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"虚拟设备 {self.device_id} 已启动")
        
    def stop(self):
        """停止设备数据发送"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info(f"虚拟设备 {self.device_id} 已停止")
        
    def _run(self):
        """设备运行循环"""
        while self.is_running:
            try:
                data = self.generate_data()
                topic = f"devices/{self.device_type}/{self.device_id}/data"
                payload = json.dumps(data)
                
                self.mqtt_client.publish(topic, payload)
                logger.info(f"设备 {self.device_id} 发送数据: {payload}")
                
                time.sleep(self.publish_interval)
            except Exception as e:
                logger.error(f"设备 {self.device_id} 发送数据错误: {e}")
                time.sleep(1)

class TemperatureHumiditySensor(VirtualDevice):
    """温湿度传感器"""
    def __init__(self, device_id, mqtt_client, publish_interval=5):
        super().__init__(device_id, "temperature_humidity", mqtt_client, publish_interval)
        self.base_temp = 25.0
        self.base_humidity = 60.0
        
    def generate_data(self):
        # 模拟温度和湿度的缓慢变化
        temp_variation = random.uniform(-2, 2)
        humidity_variation = random.uniform(-5, 5)
        
        temperature = round(self.base_temp + temp_variation, 1)
        humidity = round(max(0, min(100, self.base_humidity + humidity_variation)), 1)
        
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "temperature": temperature,
                "humidity": humidity,
                "unit_temp": "°C",
                "unit_humidity": "%"
            }
        }

class LightSensor(VirtualDevice):
    """光照传感器"""
    def __init__(self, device_id, mqtt_client, publish_interval=5):
        super().__init__(device_id, "light", mqtt_client, publish_interval)
        
    def generate_data(self):
        # 模拟光照强度（0-1000 lux）
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 18:  # 白天
            base_light = 500 + random.uniform(-200, 300)
        else:  # 夜晚
            base_light = 50 + random.uniform(-30, 50)
            
        light_intensity = max(0, round(base_light, 1))
        
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "light_intensity": light_intensity,
                "unit": "lux"
            }
        }

class MotionSensor(VirtualDevice):
    """运动传感器"""
    def __init__(self, device_id, mqtt_client, publish_interval=10):
        super().__init__(device_id, "motion", mqtt_client, publish_interval)
        
    def generate_data(self):
        # 随机生成运动检测
        motion_detected = random.choice([True, False])
        
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "motion_detected": motion_detected,
                "detection_count": random.randint(0, 5) if motion_detected else 0
            }
        }

class SmartSwitch(VirtualDevice):
    """智能开关"""
    def __init__(self, device_id, mqtt_client, publish_interval=30):
        super().__init__(device_id, "smart_switch", mqtt_client, publish_interval)
        self.is_on = False
        self.power_consumption = 0.0
        
    def generate_data(self):
        # 随机切换开关状态
        if random.random() < 0.1:  # 10%概率改变状态
            self.is_on = not self.is_on
            
        # 计算功耗
        if self.is_on:
            self.power_consumption = round(random.uniform(5, 100), 2)
        else:
            self.power_consumption = 0.0
            
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "switch_state": "ON" if self.is_on else "OFF",
                "power_consumption": self.power_consumption,
                "unit": "W"
            }
        }

class MQTTVirtualDeviceManager:
    """MQTT虚拟设备管理器"""
    def __init__(self, broker_host="localhost", broker_port=1883, username=None, password=None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client = mqtt.Client()
        self.devices = []
        self.setup_mqtt()
        
    def setup_mqtt(self):
        """设置MQTT客户端"""
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info(f"成功连接到MQTT Broker: {self.broker_host}:{self.broker_port}")
                # 订阅控制主题
                client.subscribe("devices/+/+/control")
            else:
                logger.error(f"连接MQTT Broker失败，错误代码: {rc}")
                
        def on_message(client, userdata, msg):
            try:
                topic_parts = msg.topic.split('/')
                device_type = topic_parts[1]
                device_id = topic_parts[2]
                command = json.loads(msg.payload.decode())
                logger.info(f"收到设备控制命令: {device_type}/{device_id} -> {command}")
                # 这里可以添加设备控制逻辑
            except Exception as e:
                logger.error(f"处理控制命令错误: {e}")
                
        def on_disconnect(client, userdata, rc):
            logger.warning(f"与MQTT Broker断开连接，错误代码: {rc}")
            
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
            
    def connect(self):
        """连接到MQTT Broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"连接MQTT Broker失败: {e}")
            return False
            
    def add_device(self, device):
        """添加虚拟设备"""
        self.devices.append(device)
        logger.info(f"添加虚拟设备: {device.device_id}")
        
    def start_all_devices(self):
        """启动所有虚拟设备"""
        for device in self.devices:
            device.start()
        logger.info(f"所有 {len(self.devices)} 个虚拟设备已启动")
        
    def stop_all_devices(self):
        """停止所有虚拟设备"""
        for device in self.devices:
            device.stop()
        logger.info("所有虚拟设备已停止")
        
    def disconnect(self):
        """断开MQTT连接"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("已断开MQTT连接")

def main():
    """主函数"""
    # 创建设备管理器
    # 如果你有自己的MQTT broker，请修改以下配置
    manager = MQTTVirtualDeviceManager(
        broker_host="localhost",  # 或者使用 "test.mosquitto.org" 作为测试
        broker_port=1883,
        # username="your_username",
        # password="your_password"
    )
    
    # 连接到MQTT broker
    if not manager.connect():
        print("无法连接到MQTT Broker，请检查配置")
        return
        
    # 创建虚拟设备
    devices = [
        TemperatureHumiditySensor("temp_sensor_001", manager.client, 5),
       # TemperatureHumiditySensor("temp_sensor_002", manager.client, 7),
       # LightSensor("light_sensor_001", manager.client, 8),
       # LightSensor("light_sensor_002", manager.client, 6),
       # MotionSensor("motion_sensor_001", manager.client, 10),
       # SmartSwitch("smart_switch_001", manager.client, 15),
       # SmartSwitch("smart_switch_002", manager.client, 20),
    ]
    
    # 添加设备到管理器
    for device in devices:
        manager.add_device(device)
    
    try:
        # 启动所有设备
        manager.start_all_devices()
        
        print("虚拟设备正在运行...")
        print("按 Ctrl+C 停止所有设备")
        
        # 保持程序运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n正在停止所有设备...")
        manager.stop_all_devices()
        manager.disconnect()
        print("所有设备已停止")

if __name__ == "__main__":
    main()
