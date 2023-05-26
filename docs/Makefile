# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

export TORC_URL=http://localhost:8529
export TORC_PASSWORD=openSesame
export PYTHON_CLIENT=${BUILDDIR}/python_client

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

${PYTHON_CLIENT}:
	bash ../db_service/make_api.sh
	python fix_docstring_errors.py ${PYTHON_CLIENT}/swagger_client/api/default_api.py

html: ${PYTHON_CLIENT}
	${SPHINXBUILD} -M html ${SOURCEDIR} ${BUILDDIR}

github: html
	-git branch -D gh-pages
	-git push origin --delete gh-pages
	ghp-import -n -b gh-pages -m "Update documentation" _build/html
	git checkout gh-pages
	git push --set-upstream origin gh-pages
	git checkout main
