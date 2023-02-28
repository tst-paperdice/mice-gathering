all:

formatting:
	find . -name '*.py' -not \( -path "./imports/*" -o -path "./cdktf.out/*" \) | xargs python3 -m black

define get_python_source_files
	find . -type f -name '*.py' -not -path './venv*' -not -path './imports/*'
endef

pylint:
	$(get_python_source_files) | xargs python3 -m pylint

pylint_errors:
	$(get_python_source_files) | xargs python3 -m pylint --disable=all --enable=E