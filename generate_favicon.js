// Create a canvas element
const canvas = document.createElement('canvas');
canvas.width = 32;
canvas.height = 32;

// Get the 2D drawing context
const ctx = canvas.getContext('2d');

// Draw a checkmark icon with gradient
const gradient = ctx.createLinearGradient(0, 0, 32, 32);
gradient.addColorStop(0, '#4a6bff');  
gradient.addColorStop(1, '#12c2e9');

// Background circle
ctx.fillStyle = gradient;
ctx.beginPath();
ctx.arc(16, 16, 15, 0, 2 * Math.PI);
ctx.fill();

// Checkmark
ctx.strokeStyle = 'white';
ctx.lineWidth = 3;
ctx.beginPath();
ctx.moveTo(8, 16);
ctx.lineTo(14, 22);
ctx.lineTo(24, 10);
ctx.stroke();

// Convert the canvas to a data URL
const dataUrl = canvas.toDataURL('image/png');

// Create a link to download the favicon
const link = document.createElement('a');
link.download = 'favicon.png';
link.href = dataUrl;
document.body.appendChild(link);
link.click();
document.body.removeChild(link); 