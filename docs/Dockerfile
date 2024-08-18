FROM squidfunk/mkdocs-material:latest

RUN apk add --no-cache curl ncurses make

RUN curl -fsSL https://d2lang.com/install.sh | sh -s --

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
