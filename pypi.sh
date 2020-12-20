rm -r build/ dist/ cqls.egg-info/
python3 setup.py sdist bdist_wheel &&
twine upload dist/*