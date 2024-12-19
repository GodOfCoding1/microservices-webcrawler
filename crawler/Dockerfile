FROM python:3.9
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN playwright install-deps
RUN playwright install chromium
COPY . ./
# CMD ["fastapi","run", "main.py"]