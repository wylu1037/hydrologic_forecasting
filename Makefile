.PHONY: build

build:
	@echo "🚀 Start build..."
	@pyinstaller --onefile manage.py
	@echo "🎉 Completed."

build-win:
	@echo "🚀 Start build..."
	@pyinstaller --onefile --windowed manage.py
	@echo "🎉 Completed."