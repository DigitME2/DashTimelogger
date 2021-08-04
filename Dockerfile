FROM python:3.8.5-buster

# Bind Virtual Environment
# ENV VIRTUAL_ENV=/.venvdash
# RUN python3 -m venv $VIRTUAL_ENV
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /usr/src/app
COPY . /usr/src/app

# Run the application:
CMD ["python", "appstart.py"]
