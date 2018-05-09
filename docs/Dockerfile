FROM python:3-alpine

# Install Sphinx and Pygments
RUN pip install Sphinx Pygments

# Setup directories, copy data
RUN mkdir /build
COPY . /build
WORKDIR /build/docs

# Build documentation
RUN make html

# Start webserver
WORKDIR /build/docs/_build/html
EXPOSE 8000/tcp
CMD ["python", "-m", "http.server"]
