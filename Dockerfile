# Based on the QGIS image (with Python)
FROM qgis/qgis:latest

# Set environment variables (for QGIS and testing)
ENV QGIS_PREFIX_PATH=/usr
ENV QGIS_PATH=/usr
ENV LD_LIBRARY_PATH=/usr/lib
ENV PYTHONPATH=/usr/share/qgis/python:/usr/share/qgis/python/plugins
ENV QGIS_DEBUG=0
ENV QGIS_LOG_FILE=/tmp/qgis.log
ENV PATH=/usr/bin:$PATH
ENV XDG_RUNTIME_DIR=/tmp
ENV PLUGIN_DIR=/usr/share/qgis/python/plugins

# Copy the entire plugin code into the QGIS plugins folder
COPY ./ObliczWysokosc $PLUGIN_DIR/ObliczWysokosc

# Copy the entire plugin code with tests into the plugin folder
COPY ./ /plugin

# Set the working directory
WORKDIR /plugin

RUN pip install pytest-qgis --break-system-packages

# Manual docker container usage:
    # Create the image using the Dockerfile
        #docker build -t qgis-latest .

    # Run the image with SSH and linked folders
        # docker run -it --rm -v "${PWD}/ObliczWysokosc:/usr/share/qgis/python/plugins/ObliczWysokosc" -v "${PWD}:/plugin" qgis-latest bash

    # Run the tests
        # xvfb-run -a pytest tests