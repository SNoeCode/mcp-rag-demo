# Use official Node.js image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json first to cache dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the entire project
COPY . .

# Copy environment variables
COPY .env.local /app/.env.local

# Build Next.js
RUN npm run build

# Start the application
CMD ["npm", "start"]