# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

################################
# BASE
# Sets up all our shared environment variables
################################
FROM node:lts AS builder

WORKDIR /app
COPY . /app

# Install project dependencies and build
RUN npm install
RUN npm run build


################################
# UI
# UI runtime
################################
FROM nginx:stable-alpine AS ui

ENV API_URL=http://localhost:8000

# Copy the built frontend from the builder stage...
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY env.sh /tmp/

EXPOSE 80
CMD ["/bin/sh", "-c", "chmod +x /tmp/env.sh && /tmp/env.sh /usr/share/nginx/html/env.js && nginx -g \"daemon off;\""]
