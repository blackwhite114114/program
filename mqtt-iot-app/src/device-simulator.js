const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://localhost:1883');

client.on('connect', () => {
  console.log('Device Simulator Connected');
  setInterval(() => {
    const data = { temperature: Math.random() * 30, humidity: Math.random() * 100 };
    client.publish('devices/sensor1/status', JSON.stringify(data));
    console.log('Sent data:', data);
  }, 5000); // 每5秒发送
});