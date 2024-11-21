

build:
	python -m build

requirements:
	python -m pip install --upgrade twine

upload:
	python -m twine upload --repository testpypi dist/*

clean:
	rm -rf dist
	rm -rf build
	rm -Rf src/teaml.egg-info

.PHONY: test
test:
	python -c "import teaml; tea = teaml.sample('finance101'); print(tea)"
