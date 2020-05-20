FROM python:alpine3.7 
LABEL Author="Gregory Bresolin"
COPY . /book
WORKDIR /book
RUN pip install -r requirements.txt 

# Set environment variables
ENV FLASK_APP "book"
ENV FLASK_ENV "development"

ADD . /app

# Expose the application's port
EXPOSE 5000

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]