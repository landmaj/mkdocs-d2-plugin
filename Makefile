.PHONY: clean build upload

clean:
	rm -rf build dist *.egg-info

build:
	uvx --from build pyproject-build

upload:
	uvx twine upload dist/*
