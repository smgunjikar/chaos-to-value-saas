
# Chaos-to-Value SaaS
Fullstack GPT-powered insight system.

## Frontend: React + Next.js
import Head from 'next/head';
export default function Home() {
  return (
    <>
      <Head><title>Chaos-to-Value</title></Head>
      <main className="flex flex-col items-center justify-center h-screen">
        <h1 className="text-4xl font-bold">Chaos-to-Value Platform</h1>
        <p>Enter trend or input below:</p>
        <input className="border p-2 mt-2" placeholder="e.g. AI voice tools" />
        <button className="mt-4 p-2 bg-black text-white rounded">Analyze</button>
      </main>
    </>
  );
}

{
  "name": "chaos-to-value-ui",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  }
}

## Backend: Node.js + Express + OpenAI
const express = require('express');
const trendHunter = require('./api/agents/trendHunter');
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.post('/api/agents/trendHunter', async (req, res) => {
  const input = req.body.input;
  const result = await trendHunter(input);
  res.json({ output: result });
});

app.listen(port, () => console.log(`Server running on port ${port}`));

{
  "name": "chaos-to-value-backend",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "openai": "^4.14.1"
  }
}

### Start Backend:
cd backend && npm install && npm start
const { Configuration, OpenAIApi } = require('openai');
const config = new Configuration({ apiKey: process.env.OPENAI_API_KEY });
const openai = new OpenAIApi(config);

exports.askOpenAI = async (prompt) => {
  const res = await openai.createChatCompletion({
    model: 'gpt-4o',
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.7
  });
  return res.data.choices[0].message.content;
};


### Start Frontend:
cd frontend && npm install && npm run dev
