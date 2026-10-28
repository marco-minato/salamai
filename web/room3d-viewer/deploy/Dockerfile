# Immagine statica del visualizzatore. Costruire DOPO "npm run build":
#   docker build -f deploy/Dockerfile -t salamai-room3d-viewer .
#   docker run --rm -p 127.0.0.1:8088:8080 salamai-room3d-viewer
# poi aprire http://127.0.0.1:8088/salamai/room3d/
# Sottopercorso diverso: --build-arg SUBPATH=/altro/percorso (senza / finale).
FROM nginx:1.30.5-alpine

ARG SUBPATH=/salamai/room3d
ENV SUBPATH=${SUBPATH}

COPY deploy/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY dist/ /usr/share/nginx/html${SUBPATH}/

# i file serviti non sono scrivibili dal processo nginx
RUN rm -f /etc/nginx/conf.d/default.conf \
    && chown -R root:root /usr/share/nginx/html \
    && chmod -R a-w /usr/share/nginx/html

EXPOSE 8080
