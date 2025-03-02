PACKAGE_NAME = tmp-files-collector
VERSION = 1.0.0
BUILD_DIR = build

all: build

build:
	# Clean old build
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)/DEBIAN
	mkdir -p $(BUILD_DIR)/usr/local/bin
	mkdir -p $(BUILD_DIR)/lib/systemd/system
	mkdir -p $(BUILD_DIR)/var/log

	# Copy Python script
	cp tmp_files_collector.py $(BUILD_DIR)/usr/local/bin/tmp_files_collector.py
	chmod 755 $(BUILD_DIR)/usr/local/bin/tmp_files_collector.py

	# Copy service file
	cp tmp_files_collector.service $(BUILD_DIR)/lib/systemd/system/tmp_files_collector.service

	# postinst script
	mkdir -p $(BUILD_DIR)/DEBIAN
	cp debian/postinst $(BUILD_DIR)/DEBIAN/postinst
	chmod 755 $(BUILD_DIR)/DEBIAN/postinst

	# Create control file
	echo "Package: $(PACKAGE_NAME)" > $(BUILD_DIR)/DEBIAN/control
	echo "Version: $(VERSION)" >> $(BUILD_DIR)/DEBIAN/control
	echo "Section: misc" >> $(BUILD_DIR)/DEBIAN/control
	echo "Priority: optional" >> $(BUILD_DIR)/DEBIAN/control
	echo "Architecture: all" >> $(BUILD_DIR)/DEBIAN/control
	echo "Maintainer: YourName <ramyalenin@example.com>" >> $(BUILD_DIR)/DEBIAN/control
	echo "Description: A file collector script that archives files after 10 files appear in the ./tmp directory" >> $(BUILD_DIR)/DEBIAN/control

	# Build the .deb
	dpkg-deb --build $(BUILD_DIR) $(PACKAGE_NAME)_$(VERSION).deb

install-deb:
	sudo dpkg -i $(PACKAGE_NAME)_$(VERSION).deb

clean:
	rm -rf $(BUILD_DIR) *.deb

.PHONY: all build clean install-deb
