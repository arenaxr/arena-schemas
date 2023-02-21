run: venv
	$(VENV)/python main.py

update: venv
	rm -f schemas/*.json
	$(VENV)/python updateschemas.py $(src)

docs: venv
	rm -f docs/*.md
	$(VENV)/python createdoc.py

jekyll: venv
	$(VENV)/python createjekyll.py $(dst)

dotnet: venv
	rm -f dotnet/*.cs
	$(VENV)/python createdotnet.py $(dst)

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
