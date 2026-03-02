NAME = example
STATIC_FOLDER = $(NAME)/static/
CONTENT_FOLDER = $(NAME)/content/ 
TEMPLATES_FOLDER = $(NAME)/templates/

OUTPUT_STATIC = output/$(STATIC_FOLDER)
OUTPUT_CONTENT = output/$(NAME)/

SOURCES := $(shell find $(STATIC_FOLDER) -type f) $(shell find $(CONTENT_FOLDER) -type f) build.py

.PHONY: install build run clean

install:
	@echo "Env install: RUNNING..."
	python3 -m virtualenv ./venv >/dev/null
	. ./venv/bin/activate && ./venv/bin/pip install -r requirements.txt
	@echo "Env install: DONE"

build: $(SOURCES)
	@echo "$(NAME): BUILDING..."
	mkdir -p output && mkdir -p $(OUTPUT_CONTENT) && \
		mkdir -p $(OUTPUT_STATIC) && cp -r ./$(STATIC_FOLDER)* ./$(OUTPUT_STATIC) && \
		./venv/bin/python build.py $(CONTENT_FOLDER) $(TEMPLATES_FOLDER) $(OUTPUT_CONTENT)
	@echo "$(NAME): BUILDING DONE"

run: build
	@echo "Serving $(NAME) with auto-reload: http://localhost:8000"
	. ./venv/bin/activate && watchmedo shell-command \
		--patterns="*.html;*.css;*.js;*.md" \
		--recursive \
		--command="make build" \
		$(STATIC_FOLDER) $(CONTENT_FOLDER) $(TEMPLATES_FOLDER) build.py &
	./venv/bin/python -m http.server 8000 -d $(OUTPUT_CONTENT)

clean:
	@echo "Cleaning output directory"
	rm -rf output/*

all: install build run
