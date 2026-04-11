FROM postgres:15.17-trixie

# Test password, will not be used in the final product
ENV POSTGRES_PASSWORD=12345
ENV POSTGRES_USER=dev
ENV POSTGRES_DB=dev_db

CMD ["echo", "hello, world"]