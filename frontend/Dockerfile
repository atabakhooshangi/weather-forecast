FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend application
COPY frontend/ .

# Build the application
RUN npm run build

# Expose the port the app runs on
EXPOSE 5173

# Command to run the application
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"] 