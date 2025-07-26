const express = require('express');
const mqttClient = require('../utils/mqttClient');

const router = express.Router();

// 获取设备列表（示例：静态列表）
router.get('/', (req, res) => {
  res.json([{ id: 'sensor1', name: 'Temperature Sensor' }]);
});

// 发送命令到设备
router.post('/:id/command', (req, res) => {
  const { command } = req.body;
  const topic = `devices/${req.params.id}/command`;
  mqttClient.publish(topic, JSON.stringify({ command }));
  res.json({ message: 'Command sent via MQTT' });
});

module.exports = router;