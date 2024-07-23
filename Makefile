.PHONY: build

build:
	@echo "🚀 Start build..."
	@pyinstaller --onefile manage.py
	@echo "🎉 Completed."