#COMPILE_TEMPLATE_OPTS = -d

FRONT_TEMPLATES = $(wildcard frontend/templates/*.html frontend/templates/ng-templates/*.html)
STATIC_TEMPLATES = $(subst frontend,static,$(FRONT_TEMPLATES))
JAVASCRIPT_FILES = $(wildcard frontend/src/js/app.module.js frontend/src/js/*.js)

.PHONY: all templates clean static dist javascript css

all: static

static: templates javascript css
	rsync -rupE frontend/assets/ static/

dist: static
	tar cjf static.tar.bz2 static/

clean:
	rm -rf static

templates: $(STATIC_TEMPLATES)

javascript: static/js/app.js

css: static/css/main.css

static/css/main.css: frontend/src/css/main.scss
	mkdir -p $$( dirname $@ )
	frontend/node_modules/.bin/sass $< > $@

static/js/app.js: $(JAVASCRIPT_FILES)
	mkdir -p $$( dirname $@ )
	cat $^ >$@

static/templates/%.html: frontend/templates/%.html
	mkdir -p $$( dirname $@ ) 2>/dev/null || true
	python scripts/compile_template.py ${COMPILE_TEMPLATE_OPTS} -b frontend/templates -s $< >$@
