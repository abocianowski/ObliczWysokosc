# Bazujemy na obrazie QGIS (z Pythonem)
FROM qgis/qgis:latest

# Ustaw zmienne środowiskowe (dla QGIS-a i testów)
ENV QGIS_PREFIX_PATH=/usr
ENV QGIS_PATH=/usr
ENV LD_LIBRARY_PATH=/usr/lib
ENV PYTHONPATH=/usr/share/qgis/python:/usr/share/qgis/python/plugins
ENV QGIS_DEBUG=0
ENV QGIS_LOG_FILE=/tmp/qgis.log
ENV PATH=/usr/bin:$PATH
ENV XDG_RUNTIME_DIR=/tmp
ENV PLUGIN_DIR=/usr/share/qgis/python/plugins

# Skopiuj cały kod wtyczki do folderu z wtyczkami qgisa
COPY ./ObliczWysokosc $PLUGIN_DIR/ObliczWysokosc

# Skopiuj cały kod wtyczki z testami do folderu pluginS
COPY ./ /plugin

# Ustaw katalog roboczy
WORKDIR /plugin

RUN pip install pytest-qgis --break-system-packages
# Manual docker container:
    #create image by dockerfile
        #docker build -t qgis-latest .

    # run image with ssh and linked folder
        # docker run -it --rm -v "${PWD}/ObliczWysokosc:/usr/share/qgis/python/plugins/ObliczWysokosc" -v "${PWD}:/plugin" qgis-latest bash
        # docker run -it --rm -v "${PWD}/ObliczWysokosc:/usr/share/qgis/python/plugins/ObliczWysokosc" -v "${PWD}:/plugin" -e DISPLAY=unix$DISPLAY qgis-latest

    # run tests
        # xvfb-run -a pytest tests