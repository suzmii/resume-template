ENV_FILE ?= .env
-include $(ENV_FILE)

SOURCE ?= template
SOURCE_FILE := $(if $(filter %.md,$(SOURCE)),$(SOURCE),$(SOURCE).md)
NAME := $(basename $(notdir $(SOURCE_FILE)))
TITLE ?= Resume

BUILD_DIR ?= .build
HTML := $(BUILD_DIR)/$(NAME).html
BACKGROUND_FRAGMENT := $(BUILD_DIR)/paper-background.html
PDF := $(NAME).pdf
STYLES := assets/styles/resume.css
ASSETS := \
	assets/styles/paper-background.png \
	assets/fonts/SourceHanSansCN-Regular.ttf \
	assets/fonts/SourceHanSansCN-Bold.ttf \
	assets/fonts/MapleMono-NF-CN-Regular.ttf \
	assets/fonts/iconfont.ttf

PANDOC ?= pandoc
CHROME ?= $(shell \
	if [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then \
		printf '%s' "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; \
	elif command -v google-chrome >/dev/null 2>&1; then \
		command -v google-chrome; \
	elif command -v google-chrome-stable >/dev/null 2>&1; then \
		command -v google-chrome-stable; \
	elif command -v chromium >/dev/null 2>&1; then \
		command -v chromium; \
	elif command -v chromium-browser >/dev/null 2>&1; then \
		command -v chromium-browser; \
	fi)
OPEN ?= $(shell command -v open 2>/dev/null || command -v xdg-open 2>/dev/null)
LOG := /tmp/$(NAME)-markdown-to-pdf.log

.PHONY: all pdf html preview open clean check-tools

all: pdf

pdf: $(PDF)

html: $(HTML)

$(HTML): $(SOURCE_FILE) $(STYLES) $(ASSETS) Makefile
	@command -v "$(PANDOC)" >/dev/null 2>&1 || { \
		echo "未找到 Pandoc，无法渲染 Markdown。"; \
		exit 1; \
	}
	@mkdir -p "$(BUILD_DIR)"
	@printf '%s\n' '<img class="grid-bg" src="../assets/styles/paper-background.png" alt="" aria-hidden="true">' > "$(BACKGROUND_FRAGMENT)"
	@"$(PANDOC)" "$(SOURCE_FILE)" \
		--from="gfm+raw_html" \
		--to="html5" \
		--standalone \
		--metadata pagetitle="$(TITLE)" \
		--css="../assets/styles/resume.css" \
		--include-before-body="$(BACKGROUND_FRAGMENT)" \
		--output="$@"
	@echo "wrote $(HTML)"

$(PDF): $(HTML) $(STYLES) $(ASSETS) Makefile
	@if [ ! -x "$(CHROME)" ]; then \
		echo "未找到 Chrome 或 Chromium，无法导出 PDF。"; \
		exit 1; \
	fi
	@profile=$$(mktemp -d /tmp/$(NAME)-chrome.XXXXXX); \
	tmp_pdf="$(abspath $(PDF)).tmp"; \
	rm -f "$$tmp_pdf"; \
	trap 'rm -rf "$$profile" "$$tmp_pdf"' EXIT; \
	"$(CHROME)" \
		--headless=new \
		--disable-gpu \
		--disable-crash-reporter \
		--disable-background-networking \
		--disable-component-update \
		--no-first-run \
		--no-default-browser-check \
		--allow-file-access-from-files \
		--run-all-compositor-stages-before-draw \
		--virtual-time-budget=2000 \
		--user-data-dir="$$profile" \
		--no-pdf-header-footer \
		--print-to-pdf="$$tmp_pdf" \
		"file://$(abspath $(HTML))" >"$(LOG)" 2>&1 & \
	pid=$$!; \
	last_size=0; stable=0; \
	for i in $$(seq 1 160); do \
		if [ -s "$$tmp_pdf" ]; then \
			size=$$(wc -c <"$$tmp_pdf"); \
			if [ "$$size" -eq "$$last_size" ]; then stable=$$((stable + 1)); else stable=0; fi; \
			last_size=$$size; \
			if [ "$$stable" -ge 4 ]; then break; fi; \
		fi; \
		sleep 0.25; \
	done; \
	kill $$pid 2>/dev/null || true; \
	wait $$pid 2>/dev/null || true; \
	if [ ! -s "$$tmp_pdf" ] || [ "$$stable" -lt 4 ]; then \
		cat "$(LOG)"; \
		echo "PDF export failed"; \
		exit 1; \
	fi; \
	mv -f "$$tmp_pdf" "$(PDF)"; \
	rm -rf "$$profile"; \
	trap - EXIT; \
	echo "wrote $(PDF)"

preview: $(HTML)
	@if [ -z "$(OPEN)" ]; then echo "未找到系统打开命令"; exit 1; fi
	@"$(OPEN)" "$(HTML)"

open: $(PDF)
	@if [ -z "$(OPEN)" ]; then echo "未找到系统打开命令"; exit 1; fi
	@"$(OPEN)" "$(PDF)"

check-tools:
	@command -v "$(PANDOC)" >/dev/null 2>&1 && echo "$$(command -v "$(PANDOC)")" || { \
		echo "未找到 Pandoc"; \
		exit 1; \
	}
	@if [ -n "$(CHROME)" ] && [ -x "$(CHROME)" ]; then \
		echo "$(CHROME)"; \
	else \
		echo "未找到 Chrome 或 Chromium，可通过 CHROME=/path/to/chrome 指定"; \
		exit 1; \
	fi

clean:
	rm -rf "$(BUILD_DIR)"
	rm -f "$(PDF)"
	rm -f "$(LOG)"
