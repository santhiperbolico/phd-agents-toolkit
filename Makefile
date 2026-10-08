PYTHON ?= python3.11
PREFIX ?= $(HOME)/.local
VENV := $(PREFIX)/share/phd-agents-mcp/venv
CURSOR_SKILLS := $(HOME)/.cursor/skills
CURSOR_HELPERS := /usr/share/cursor/resources/app/resources/helpers
MCP_PATH := $(PREFIX)/bin:$(CURSOR_HELPERS):/usr/bin:/bin
CLAUDIA_DOCS_PATH ?= $(HOME)/Trabajo/repositorios/claudia_devenv/claudia_docs
PHD_TOOLKIT_ROOT ?= $(CURDIR)
PHD_DOCS_HOME ?= $(HOME)/.phd-docs

.PHONY: help install-mcp install-zotero install-phd-docs sync-phd-docs uninstall-mcp uninstall-phd-docs test-phd-docs

help:
	@echo "install-mcp       Install Overleaf/Taurus/UPM-mail/Slack-session CLIs and skills"
	@echo "install-zotero    Install zotero-mcp (PyPI) and the zotero-phd skill"
	@echo "install-phd-docs  Install phd-docs RAG CLI, MCP, and phd-rag-docs skill"
	@echo "sync-phd-docs     Re-index notes/, docs/, and Zotero PDFs"
	@echo "test-phd-docs     Run phd-docs unit tests"
	@echo "uninstall-mcp     Remove MCP CLIs, skill links, and the shared venv"
	@echo "uninstall-phd-docs Remove phd-docs CLI, MCP link, and skill link"

$(VENV)/bin/python:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install -U pip

install-mcp: $(VENV)/bin/python
	mkdir -p $(PREFIX)/bin $(CURSOR_SKILLS)
	$(VENV)/bin/pip install -e $(CURDIR)/mcp/overleaf -e $(CURDIR)/mcp/taurus -e $(CURDIR)/mcp/upm-mail -e "$(CURDIR)/mcp/slack-session[auth]"
	ln -sfn $(VENV)/bin/overleaf-tools $(PREFIX)/bin/overleaf-tools
	ln -sfn $(VENV)/bin/taurus-tools $(PREFIX)/bin/taurus-tools
	ln -sfn $(VENV)/bin/upm-mail-tools $(PREFIX)/bin/upm-mail-tools
	ln -sfn $(VENV)/bin/slack-session-tools $(PREFIX)/bin/slack-session-tools
	ln -sfn $(CURDIR)/mcp/overleaf/skill $(CURSOR_SKILLS)/overleaf-mcp
	ln -sfn $(CURDIR)/mcp/taurus/skill $(CURSOR_SKILLS)/taurus-cluster
	ln -sfn $(CURDIR)/mcp/upm-mail/skill $(CURSOR_SKILLS)/upm-mail
	ln -sfn $(CURDIR)/mcp/slack-session/skill $(CURSOR_SKILLS)/slack-session
	@echo
	@echo "Installed:"
	@echo "  $(PREFIX)/bin/overleaf-tools"
	@echo "  $(PREFIX)/bin/taurus-tools"
	@echo "  $(PREFIX)/bin/upm-mail-tools"
	@echo "  $(PREFIX)/bin/slack-session-tools"
	@echo "  $(CURSOR_SKILLS)/overleaf-mcp"
	@echo "  $(CURSOR_SKILLS)/taurus-cluster"
	@echo "  $(CURSOR_SKILLS)/upm-mail"
	@echo "  $(CURSOR_SKILLS)/slack-session"
	@echo
	@echo "Slack session auth (once): $(VENV)/bin/playwright install chromium"
	@echo "Merge mcp/mcp.json.example into ~/.cursor/mcp.json then reload Cursor."
	@echo "If Cursor does not expand ~, replace it with $(HOME)."
	@echo "Suggested PATH for mcp.json: $(MCP_PATH)"

install-zotero: $(VENV)/bin/python
	mkdir -p $(PREFIX)/bin $(CURSOR_SKILLS)
	$(VENV)/bin/pip install zotero-mcp-server
	ln -sfn $(VENV)/bin/zotero-mcp $(PREFIX)/bin/zotero-mcp
	ln -sfn $(CURDIR)/mcp/zotero/skill $(CURSOR_SKILLS)/zotero-phd
	@echo
	@echo "Installed: $(PREFIX)/bin/zotero-mcp"
	@echo "Skill:     $(CURSOR_SKILLS)/zotero-phd"
	@echo "Keep Zotero desktop open (local API on 127.0.0.1:23119)."
	@echo "Merge mcp/zotero/mcp.json.example into ~/.cursor/mcp.json then reload Cursor."

install-phd-docs: $(VENV)/bin/python
	mkdir -p $(PREFIX)/bin $(CURSOR_SKILLS)
	$(VENV)/bin/pip install -e "$(CLAUDIA_DOCS_PATH)" -e "$(CURDIR)/phd_docs[pdf,dev]"
	ln -sfn $(VENV)/bin/phd-docs $(PREFIX)/bin/phd-docs
	ln -sfn $(VENV)/bin/phd-docs-mcp $(PREFIX)/bin/phd-docs-mcp
	ln -sfn $(CURDIR)/mcp/phd-docs/skill $(CURSOR_SKILLS)/phd-rag-docs
	@echo
	@echo "Installed:"
	@echo "  $(PREFIX)/bin/phd-docs"
	@echo "  $(PREFIX)/bin/phd-docs-mcp"
	@echo "  $(CURSOR_SKILLS)/phd-rag-docs"
	@echo
	@echo "Merge mcp/phd-docs/mcp.json.example into ~/.cursor/mcp.json then reload Cursor."
	@echo "Then run: make sync-phd-docs"

sync-phd-docs:
	PHD_TOOLKIT_ROOT="$(PHD_TOOLKIT_ROOT)" PHD_DOCS_HOME="$(PHD_DOCS_HOME)" \
		PHD_DOCS_EMBEDDING_DEVICE=cpu \
		$(VENV)/bin/phd-docs sync

test-phd-docs: install-phd-docs
	cd phd_docs && $(VENV)/bin/python -m pytest

uninstall-mcp:
	rm -f $(PREFIX)/bin/overleaf-tools $(PREFIX)/bin/taurus-tools $(PREFIX)/bin/upm-mail-tools $(PREFIX)/bin/slack-session-tools $(PREFIX)/bin/zotero-mcp
	rm -f $(CURSOR_SKILLS)/overleaf-mcp $(CURSOR_SKILLS)/taurus-cluster $(CURSOR_SKILLS)/upm-mail $(CURSOR_SKILLS)/slack-session $(CURSOR_SKILLS)/zotero-phd
	rm -rf $(PREFIX)/share/phd-agents-mcp

uninstall-phd-docs:
	rm -f $(PREFIX)/bin/phd-docs $(PREFIX)/bin/phd-docs-mcp
	rm -f $(CURSOR_SKILLS)/phd-rag-docs
