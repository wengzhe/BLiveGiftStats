FROM python:3.8.13-bullseye
ARG BASE_PATH='/root/blive-gift-stats'
ARG EXT_DATA_PATH='/mnt/data'
WORKDIR "${BASE_PATH}"

# 后端依赖
COPY blivedm/requirements.txt blivedm/
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 数据目录
COPY . ./
RUN mv data "${EXT_DATA_PATH}" \
    && ln -s "${EXT_DATA_PATH}" data

# 运行
VOLUME "${EXT_DATA_PATH}"
ENTRYPOINT ["python3", "main.py"]
