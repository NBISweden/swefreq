#COMPILE_TEMPLATE_OPTS = -d

FRONT_TEMPLATES = $(wildcard frontend/templates/*.html frontend/templates/ng-templates/*.html)
STATIC_TEMPLATES = $(subst frontend,static,$(FRONT_TEMPLATES))

.PHONY: all templates clean static dist

all: static

static: templates
	rm -rf frontend/dist
	cd frontend && ./node_modules/.bin/grunt
	rsync -rupE frontend/dist/ static/

dist: static
	tar cjf static.tar.bz2 static/

clean:
	rm -rf static

templates: $(STATIC_TEMPLATES)

static/templates/%.html: frontend/templates/%.html
	mkdir -p $$( dirname $@ ) 2>/dev/null || true
	python scripts/compile_template.py ${COMPILE_TEMPLATE_OPTS} -b frontend/templates -s $< >$@
