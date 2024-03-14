#!/bin/sh

TARGET=$1

echo "window._env_ = {" > ${TARGET}
echo "    API_URL: \"${API_URL}\"," >> ${TARGET}
echo "};" >> ${TARGET}
