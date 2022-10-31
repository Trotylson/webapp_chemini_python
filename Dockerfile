FROM alpine:latest
COPY . /app

WORKDIR /app

RUN apk add py3-pip
RUN pip install -r requirements

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--reload"]
# python3 -m uvicorn main:app --host="0.0.0.0" --port="8001" --reload