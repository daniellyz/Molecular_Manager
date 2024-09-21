FROM python:3.10-alpine
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod 666 compounds.db
EXPOSE 5000
CMD ["python", "app.py"]