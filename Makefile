run: venv
	$(VENV)/python build_schemas.py main

update: venv
	rm -f schemas/*.json
	$(VENV)/python build_schemas.py update $(src)

docs: venv
	rm -f docs/*.md
	$(VENV)/python build_schemas.py doc

jekyll: venv
	$(VENV)/python build_schemas.py jekyll $(dst)

dotnet: venv
	$(VENV)/python build_schemas.py dotnet $(src) $(dst)

py: venv
	$(VENV)/python build_schemas.py py $(src) $(dst)

show-req: venv
		$(VENV)/pip freeze

freeze: venv
				$(VENV)/pip freeze > requirements.txt

include Makefile.venv
Makefile.venv:
	curl \
		-o Makefile.fetched \
		-L "https://github.com/sio/Makefile.venv/raw/v2020.08.14/Makefile.venv"
	echo "5afbcf51a82f629cd65ff23185acde90ebe4dec889ef80bbdc12562fbd0b2611 *Makefile.fetched" \
		| shasum -a 256 --check - \
		&& mv Makefile.fetched Makefile.venv
