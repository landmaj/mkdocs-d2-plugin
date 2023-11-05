FROM squidfunk/mkdocs-material:latest

RUN apk add --no-cache curl ncurses make

RUN curl -fsSL https://d2lang.com/install.sh | sh -s --
RUN pip install mkdocs-d2-plugin==1.0.0
