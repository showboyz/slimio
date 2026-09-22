FROM node:20-slim

RUN apt-get update && \
     apt-get install -y --no-install-recommends ghostscript && \
     rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json ./
COPY public ./public
COPY server ./server

ENV PORT=3001
ENV HOST=0.0.0.0

EXPOSE 3001

CMD ["node", "server/server.cjs"]
