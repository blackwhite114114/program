const express = require('express');
const cors = require('cors');
require('dotenv').config();
const mqttClient = require('./utils/mqttClient');
const deviceRoutes = require('./routes/deviceRoutes');

const app = express();
app.use(cors());
app.use(express.json());

// 示例：MQTT 消息处理（扩展这里）
mqttClient.on('message', (topic, message) => {
  const data = JSON.parse(message.toString());
  // 简单处理：打印数据（你可以保存到文件或数据库）
  console.log(`Processed data: ${JSON.stringify(data)}`);
});

// 路由
app.use('/api/devices', deviceRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));