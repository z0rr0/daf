NAME=daf
HOST=127.0.0.1
PORT=8002
ADDR=127.0.0.1
MANAGE=daf/manage.py
PID=/tmp/.$(NAME).pid

all: test

test:
	python $(MANAGE) test

start:
	@echo "  >  $(NAME)"
	python $(MANAGE) runserver --noreload $(HOST):$(PORT) & echo $$! > $(PID)
	@-cat $(PID)
	@echo "  >  http://$(ADDR):$(PORT)"

stop:
	@-touch $(PID)
	@-cat $(PID)
	@-kill `cat $(PID)` || true
	@-rm $(PID)

restart: stop start