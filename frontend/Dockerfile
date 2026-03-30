FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Environment variables could be provided via compose
ENV NEXT_PUBLIC_API_URL=http://localhost:3001/api

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
