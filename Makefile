dev-requirements:
	pip-compile --resolver backtracking -o dev.txt dev.in

sync:
	pip-sync dev.txt

ganache:
	yarn add ganache

dlt-1:
	yarn run ganache -p 8545

dlt-2:
	yarn run ganache -p 8546
