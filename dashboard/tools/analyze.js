const readline = require('readline');

function extractKeywords(text) {
  // Simple: split by space, remove duplicates, sort by frequency
  const words = text.toLowerCase().match(/\w+/g) || [];
  const freq = {};
  words.forEach(w => freq[w] = (freq[w] || 0) + 1);
  return Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([word]) => word);
}

const rl = readline.createInterface({ input: process.stdin });
let input = '';
rl.on('line', line => input += line);
rl.on('close', () => {
  try {
    const data = JSON.parse(input);
    const text = data.text || '';
    const keywords = extractKeywords(text);
    console.log(JSON.stringify({ keywords }));
  } catch (e) {
    console.log(JSON.stringify({ error: e.toString() }));
  }
});