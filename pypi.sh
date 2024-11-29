if [ "$OSTYPE" == "msys" ]; then
    bc() {
        /c/Users/rd/bin/unix/bc/bin/bc.exe "$@"
    }
fi

# Build package
[[ -d build/ ]] && rm -r build/ 
[[ -d dist/ ]] && rm -r dist/
[[ -d nutrical.egg-info/ ]] && rm -r nutrical.egg-info/
python setup.py sdist bdist_wheel &&
twine upload --verbose --repository pypi dist/*
