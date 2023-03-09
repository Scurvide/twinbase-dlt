dev-requirements:
	pip-compile --resolver backtracking -o dev.txt dev.in

sync:
	pip-sync dev.txt

dlt:
	yarn add ganache
	yarn run ganache