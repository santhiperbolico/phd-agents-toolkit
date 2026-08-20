PYTHON ?= python3.11
PREFIX ?= $(HOME)/.local
VENV := $(PREFIX)/share/phd-agents-mcp/venv
CURSOR_SKILLS := $(HOME)/.cursor/skills
CURSOR_HELPERS := /usr/share/cursor/resources/app/resources/helpers
MCP_PATH := $(PREFIX)/bin:$(CURSOR_HELPERS):/usr/bin:/bin

.PHONY: help install-mcp install-zotero uninstall-mcp

help:
	@echo "install-mcp     Install Overleaf/Taurus CLIs and their Cursor skills"
	@echo "install-zotero  Install zotero-mcp (PyPI) and the zotero-phd skill"
	@echo "uninstall-mcp   Remove CLIs, skill links, and the shared venv"

$(VENV)/bin/python:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install -U pip

install-mcp: $(VENV)/bin/python
	mkdir -p $(PREFIX)/bin $(CURSOR_SKILLS)
	$(VENV)/bin/pip install -e $(CURDIR)/mcp/overleaf -e $(CURDIR)/mcp/taurus
	ln -sfn $(VENV)/bin/overleaf-tools $(PREFIX)/bin/overleaf-tools
	ln -sfn $(VENV)/bin/taurus-tools $(PREFIX)/bin/taurus-tools
	ln -sfn $(CURDIR)/mcp/overleaf/skill $(CURSOR_SKILLS)/overleaf-mcp
	ln -sfn $(CURDIR)/mcp/taurus/skill $(CURSOR_SKILLS)/taurus-cluster
	@echo
	@echo "Installed:"
	@echo "  $(PREFIX)/bin/overleaf-tools"
	@echo "  $(PREFIX)/bin/taurus-tools"
	@echo "  $(CURSOR_SKILLS)/overleaf-mcp"
	@echo "  $(CURSOR_SKILLS)/taurus-cluster"
	@echo
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

uninstall-mcp:
	rm -f $(PREFIX)/bin/overleaf-tools $(PREFIX)/bin/taurus-tools $(PREFIX)/bin/zotero-mcp
	rm -f $(CURSOR_SKILLS)/overleaf-mcp $(CURSOR_SKILLS)/taurus-cluster $(CURSOR_SKILLS)/zotero-phd
	rm -rf $(PREFIX)/share/phd-agents-mcp
