.PHONY: install dev test clean build publish

install:
	pip install -e .

dev:
	pip install -e .[dev]

test:
	pytest tests/ -v --cov=rewind --cov-report=term-missing

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f *.db

build: clean
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*

demo-record:
	python examples/demo_simple.py

demo-replay:
	rewind replay demo.trace

demo-advanced:
	python examples/demo_time_travel.py

demo-diff:
	rewind diff demo.trace 0 5

demo-search:
	rewind search demo.trace result