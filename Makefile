.PHONY: clean build upload

clean:
	rm -rf build dist *.egg-info

build:
	python3 -m build

upload:
	python3 -m twine upload dist/*
