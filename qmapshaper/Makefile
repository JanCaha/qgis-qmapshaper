.PHONY: zip

prepare: clean delete

zip: prepare zipfiles

delete:
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf

clean:
	py3clean .

zipfiles:
	pb_tool zip