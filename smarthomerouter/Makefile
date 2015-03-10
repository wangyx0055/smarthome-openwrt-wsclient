#
# Copyright (C) 2013-2014 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=smarthomerouter
PKG_RELEASE:=1

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)
PKG_INSTALL_DIR:=$(PKG_BUILD_DIR)/ipkg-install

include $(INCLUDE_DIR)/kernel.mk
include $(INCLUDE_DIR)/package.mk

define Package/smarthomerouter
	SECTION:=smarthomerouter
	CATEGORY:=Smarthomerouter
	TITLE:=smarthomerouter
	DEPENDS:=+python +python-curl
	PKGARCH:=all
endef

define Package/smarthomerouter/description
	This is the websocket server in router.
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./files/* $(PKG_BUILD_DIR)/
endef

define Build/Compile
	true
endef

define Package/smarthomerouter/install
	$(INSTALL_DIR) $(1)/usr/sbin
	$(CP) ./files/usr/sbin/* $(1)/usr/sbin/
endef

$(eval $(call BuildPackage,smarthomerouter))

