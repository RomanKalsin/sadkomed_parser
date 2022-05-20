install:
		poetry install
sadkomed_parser:
		poetry run sadkomed_parser 
build:
		poetry build
package-install:
		python3 -m pip install --user dist/*.whl
package-uninstall:
		python3 -m pip uninstall sadkomed_parser
publish:
		poetry publish --dry-run