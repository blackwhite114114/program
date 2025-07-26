const mqtt = require('mqtt');
require('dotenv').config();

const client = mqtt.connect(process.env.MQTT_BROKER_URL, {
  clientId: 'node-server-' + Math.random().toString(16).substr(2, 8),
  reconnectPeriod: 1000, // 自动重连
});

client.on('connect', () => {
  console.log('Connected to Mosquitto Broker');
  client.subscribe('devices/+/status', (err) => {
    if (!err) console.log('Subscribed to device status topics');
  });
});

client.on('message', (topic, message) => {
  console.log(`Received from ${topic}: ${message.toString()}`);
  // 这里可以添加处理逻辑，如保存数据到文件或数据库
});

client.on('error', (err) => {
  console.error('MQTT Connection Error:', err);
});

module.exports = client;