###########################################################################
## GENERIC TEMPLATE - USAGE
###########################################################################
# The following variables should be set in your makefile before including
# this file.
### Library version.  Must use Semantic Versioning 'x.y.z'.  E.g. '0.1.0'
#LIB_MAJOR_VER = 0
#LIB_MINOR_VER = 1
#LIB_PATCH_VER = 0
#
### Name of the library (do not prefix with 'lib'), e.g. MyUtil
#TARGET_NAME = MyUtil
#
### List of private source files (do not include file extensions)
### Do not put public header files in the list, only private ones.
#CPP_SRC_LIST =
#C_SRC_LIST =
#H_SRC_LIST =
### API_HEADER_LIST contains all public header files, *excluding* the $(TARGET_NAME).h file.
#API_HEADER_LIST =
#
### List of System Lib Folders. "-l" will be prepended to each element.
#PKG_LIST =
### example = el-lib/libSysUtil.git el-lib/libVidUtil.git
#DEP_BUILD_LIST =
#SYS_INC_DIRS =
#SYS_LIBS_DIRS =
### example GLEW glfw GL freetype X11 Xxf6vm Xrandr pthread Xi jpeg m
#SYS_DYN_LIBS_LIST =
#SYS_STAT_LIBS_LIST =
#
### To use sysroot, either define the environment variable externally, or set it manually
# SYSROOT =


###########################################################################
## GENERIC TEMPLATE - DO NOT EDIT
###########################################################################

###########################################################################
## Useful functions for parsing strings like 'repo.git', 'mybranch!repo.git'
# Returns the .git repo after optional separator [mybranch!]repo.git
repo = $(lastword $(subst !, ,$1))
# Returns the branch in 'mybranch!repo.git' if present, otherwise master
branch = $(if $(word 2,$(subst !, ,$1)), $(firstword $(subst !, ,$1)),master)

# define a newline, note, that two blank lines are required!
define NL


endef
###########################################################################

STATIC_ONLY = 1

# Check for environment variables.
ifndef SHELL
SHELL = /usr/bin/sh
endif

ifndef ARCH
ARCH = $(shell uname -m)
endif

ifndef OS_SIZE
OS_SIZE = $(shell getconf LONG_BIT)
$(info INFO: OS_SIZE not specified. Using host size)
endif

# Python Related
export PYTHON ?= python3
export PYTHON_SCRIPTS_DIR ?= $(CURDIR)/teensylibs_build_engine/python/buildScripts

# Set default makefile name
MAKEFILE_NAME ?= Makefile

CC      = $(TOOL_PREFIX)gcc
CXX     = $(TOOL_PREFIX)g++
AS      = $(TOLL_PREFIX)as
AR      = $(TOOL_PREFIX)gcc-ar
LD      = $(TOOL_PREFIX)ld
OBJCOPY = $(TOOL_PREFIX)objcopy

ifndef DESTDIR
DESTDIR =$(DIST_ARCHDIR)
endif

# Setup the directory structure
DISTDIR      = $(CURDIR)/dist/
API_INCDIR   = $(CURDIR)/$(REPO_DIR)/$(TARGET_NAME)
LOCAL_INCDIR = $(CURDIR)/$(REPO_DIR)/$(TARGET_NAME)
SRCDIR       = $(CURDIR)/$(REPO_DIR)/$(TARGET_NAME)
# dependency dir can come from the environment
export DEPDIR ?= $(CURDIR)/deps
PATCH_DIR    = $(CURDIR)/patches/$(TARGET_NAME)

# Define the output directories
OBJDIR = $(CURDIR)/obj/$(ARCH)/$(TARGET_NAME)/
# DISTDIR can come from the environment
export DISTDIR = $(CURDIR)/dist
export DIST_ARCHDIR ?= $(CURDIR)/dist/$(ARCH)
PREFIX ?= /
DIST_LIBDIR ?= $(DIST_ARCHDIR)$(PREFIX)/lib/
DIST_INCDIR ?= $(DIST_ARCHDIR)$(PREFIX)/include
OUTPUT_DIRS = $(DIST_ARCHDIR) $(DIST_LIBDIR) $(DIST_INCDIR) $(DIST_INCDIR)/$(TARGET_NAME) $(OBJDIR) $(OBJDIR)/src $(OBJDIR)/utility $(DEPDIR) $(OBJDIR)/src/$(API_HEADER_CUSTOM_DIR_NAME)
OUTPUT_DIRS += $(DIST_INCDIR)/$(TARGET_NAME) $(DIST_INCDIR)/$(TARGET_NAME)/utility $(DIST_INCDIR)/$(TARGET_NAME)/$(API_HEADER_CUSTOM_DIR_NAME)
MKDIR_P = mkdir -p

# Compiler and Linker settings
COMMON_FLAGS +=

# Preprocessor flags
CPPFLAGS += -c -Wall $(COMMON_FLAGS)
CPPFLAGS += -ffunction-sections -fdata-sections -fno-exceptions
CPPFLAGS += -Wno-error=narrowing
CPPFLAGS += -mthumb -mcpu=cortex-m7 -mfloat-abi=hard -mfpu=fpv5-d16
CPPFLAGS += -nostdlib
CPPFLAGS += -D__IMXRT1062__ -DTEENSYDUINO=156 -DARDUINO=10819 -DF_CPU=600000000 -DLAYOUT_US_ENGLISH
CPPFLAGS += -DAUDIO_BLOCK_SAMPLES=128 -DAUDIO_SAMPLE_RATE_EXACT=48000.0f

ifndef AVALON_REV
export AVALON_REV=1
endif

ifeq ($(AVALON_REV),1)
CPPFLAGS += -DARDUINO_TEENSY41
endif

ifeq ($(AVALON_REV),2)
CPPFLAGS += -DARDUINO_TEENSY_MICROMOD
endif

CPPFLAGS += $(SYS_INC_DIRS) -I$(API_INCDIR) -I$(LOCAL_INCDIR) -I$(DIST_INCDIR)

# The core repo is special and it's path is manually included
CPPFLAGS  += -I$(DIST_INCDIR)/cores

TEENSYLIBS_INCLUDE_LIST = Adafruit-GFX-Library Adafruit_BusIO Audio Bounce2 Encoder Wire SPI TeensyThreads WDT_T4 Teensy-4.x-Quad-Encoder-Library LittleFS
TEENSYLIBS_INCLUDE_PATHS = $(addprefix -I$(DIST_INCDIR)/, $(TEENSYLIBS_INCLUDE_LIST))
CPPFLAGS += $(TEENSYLIBS_INCLUDE_PATHS)

# include all subdirs in the repo 'inc' folder
#CPPFLAGS += -I$(dir $(wildcard $(DIST_INCDIR)/*))
#CPPFLAGS += $(addprefix -I, $(shell find $(DIST_INCDIR) -type d))
#CPPFLAGS += -I/home/blackaddr/Apps/arduino-1.8.12/hardware/teensy/avr/cores/teensy4


# note ARM EABI compiler doesn't support -march option
CFLAGS   += -std=gnu99 $(COMMON_FLAGS)
CXXFLAGS += -std=gnu++17 -fpermissive -fno-rtti -fno-threadsafe-statics -felide-constructors

# Archiver flags
ARFLAGS   = -cr

DEBUGFLAGS     = -g -O0 -D_DEBUG -DUSB_DUAL_SERIAL
RELEASEFLAGS   = -O2 -D NDEBUG -DUSB_MIDI_AUDIO_SERIAL
DEFAULTFLAGS   = -O2 -D NDEBUG -DUSB_MIDI_AUDIO_SERIAL

DYN_TARGET_LIST = lib$(TARGET_NAME).so.$(LIB_VER)
STATIC_TARGET_LIST = lib$(TARGET_NAME).a

#Prepend the path
SYS_DYN_LIBS     = -L$(DIST_LIBDIR) $(SYS_LIBS_DIRS) $(addprefix -l, $(SYS_DYN_LIBS_LIST))
SYS_STAT_LIBS    = -L$(DIST_LIBDIR) $(SYS_LIBS_DIRS) $(addprefix -l, $(SYS_STAT_LIBS_LIST))
API_HEADERS      = $(addsuffix .h, $(addprefix $(API_INCDIR), $(API_HEADER_LIST)))
API_HPP_HEADERS  = $(addsuffix .hpp, $(addprefix $(API_INCDIR), $(API_HEADER_HPP_LIST)))
API_TPP_HEADERS  = $(addsuffix .tpp, $(addprefix $(API_INCDIR), $(API_HEADER_TPP_LIST)))
API_UTIL_HEADERS = $(addsuffix .h, $(addprefix $(API_INCDIR), $(API_HEADER_UTIL_LIST)))
API_CUSTOM_HEADERS = $(addsuffix .h, $(addprefix $(API_INCDIR), $(API_HEADER_CUSTOM_LIST)))
API_HEADER_DIRS  = $(addprefix $(API_INCDIR), $(API_HEADER_DIRS_LIST))
LOCAL_HEADERS   += $(addsuffix .h, $(addprefix $(LOCAL_INCDIR), $(H_SRC_LIST)))
SOURCES_CPP      = $(addsuffix .cpp, $(addprefix $(SRCDIR), $(CPP_SRC_LIST)))
SOURCES_UTIL_CPP = $(addsuffix .cpp, $(addprefix $(SRCDIR), $(CPP_SRC_UTIL_LIST)))
SOURCES_C        = $(addsuffix .c, $(addprefix $(SRCDIR), $(C_SRC_LIST)))
SOURCES_S        = $(addsuffix .S, $(addprefix $(SRCDIR), $(S_SRC_LIST)))

# Some Teensy libs use 'src' subfolder, some do not. It must be removed from the object paths
OBJECTS_CPP  = $(addsuffix .o, $(addprefix $(OBJDIR), $(CPP_SRC_LIST)))
OBJECTS_CPP += $(addsuffix .o, $(addprefix $(OBJDIR), $(CPP_SRC_UTIL_LIST)))
OBJECTS_C    = $(addsuffix .o, $(addprefix $(OBJDIR), $(C_SRC_LIST)))
OBJECTS_S    = $(addsuffix .o, $(addprefix $(OBJDIR), $(S_SRC_LIST)))

PREPROC_DEFINES = $(addprefix -D, $(PREPROC_DEFINES_LIST))

ifeq ($(NO_PRINTF),1)
PREPROC_DEFINES += -DNO_PRINTF
endif

CPPFLAGS += $(PREPROC_DEFINES)

# Create a list of the examples based on directories
EXAMPLE_DIRS = $(sort $(dir $(wildcard ./examples/*/)))

DYN_TARGET =  $(addprefix $(DIST_LIBDIR), $(DYN_TARGET_LIST))
STATIC_TARGET = $(addprefix $(DIST_LIBDIR), $(STATIC_TARGET_LIST))

ifdef STATIC_ONLY
DYN_TARGET =
endif

all: build_engine_ver directories api_headers  $(DYN_TARGET) $(STATIC_TARGET)
all-nodeps : directories api_headers $(DYN_TARGET)_nodeps $(STATIC_TARGET)_nodeps

build_engine_ver :
	@cd $(TEENSY_BUILD_ENGINE_LOC) && \
	echo "TEENSY_BUILD_ENGINE_LOC: $(TEENSY_BUILD_ENGINE_LOC)" && \
	echo "TEENSY BUILD ENGINE GIT BRANCH: `git symbolic-ref -q --short HEAD || git describe --tags --exact-match` : `git rev-parse --verify HEAD`"

directories:
	$(MKDIR_P) $(OUTPUT_DIRS)
	$(ifneq $(strip $(OBJECTS_CPP)),) $(MKDIR_P) $(dir $(OBJECTS_CPP)) endif
	$(ifneq $(strip $(OBJECTS_C  )),) $(MKDIR_P) $(dir $(OBJECTS_C  )) endif
	$(ifneq $(strip $(OBJECTS_S  )),) $(MKDIR_P) $(dir $(OBJECTS_S  )) endif

symlinks:
	ln -f -s lib$(TARGET_NAME).so.$(LIB_VER) $(DIST_LIBDIR)/lib$(TARGET_NAME).so
	ln -f -s lib$(TARGET_NAME).so.$(LIB_VER) $(DIST_LIBDIR)/lib$(TARGET_NAME).so.$(LIB_MAJOR_VER)
	ln -f -s lib$(TARGET_NAME).so.$(LIB_VER) $(DIST_LIBDIR)/lib$(TARGET_NAME).so.$(LIB_MAJOR_VER).$(LIB_MINOR_VER)

api_headers: directories
	$(foreach header,$(API_HEADERS), cp -f $(header) $(DIST_INCDIR)/$(TARGET_NAME)/ $(NL))
	$(foreach header,$(API_UTIL_HEADERS), cp -f $(header) $(DIST_INCDIR)/$(TARGET_NAME)/utility/ $(NL))
	$(foreach header,$(API_HPP_HEADERS), cp -f $(header) $(DIST_INCDIR)/$(TARGET_NAME)/ $(NL))
	$(foreach header,$(API_TPP_HEADERS), cp -f $(header) $(DIST_INCDIR)/$(TARGET_NAME)/ $(NL))
	$(foreach header,$(API_CUSTOM_HEADERS), cp -f $(header) $(DIST_INCDIR)/$(TARGET_NAME)/$(API_HEADER_CUSTOM_DIR_NAME)/ $(NL))
	$(foreach header_dir,$(API_HEADER_DIRS), cp -af $(header_dir) $(DIST_INCDIR)/$(TARGET_NAME)/ $(NL))

$(STATIC_TARGET): deps $(OBJECTS_C) $(OBJECTS_CPP) $(OBJECTS_S)
	$(AR) $(ARFLAGS) $(STATIC_TARGET) $(OBJECTS_C) $(OBJECTS_CPP) $(OBJECTS_S)

debug: DEFAULTFLAGS   = $(DEBUGFLAGS)
debug: all

release: DEFAULTFLAGS   = $(RELEASEFLAGS)
release: all

#profile: CFLAGS += -pg
#profile: CXXFLAGS += -pg
#profile: DEFAULTFLAGS   = $(RELEASEFLAGS)
#profile: all

clean:
	-rm -f $(OBJECTS_C) $(OBJECTS_CPP) $(OBJECTS_S)
	-rm -f $(DYN_TARGET) $(STATIC_TARGET)

distclean: clean
	-$(foreach rep, $(DEP_BUILD_LIST), make -C $(DEPDIR)/$(call repo,$(rep)) clean;)
	-rm -rf $(DIST_ARCHDIR)

mrproper: clean
	-rm -rf $(DEPDIR) $(DIST_ARCHDIR) $(OBJDIR) $(CURDIR)/libs/*
	git submodule init && git submodule update

veryclean: distclean

set-install-local:
	export DESTDIR=$(CURDIR)/dist/$(ARCH)
install: all
	$(MKDIR_P) $(DESTDIR)$(PREFIX)/lib
	$(MKDIR_P) $(DESTDIR)$(PREFIX)/include
	$(MKDIR_P) $(DESTDIR)$(PREFIX)/include/$(TARGET_NAME)
ifndef STATIC_ONLY
	@if ! [ $(DYN_TARGET) -ef $(DESTDIR)$(PREFIX)/lib/$(DYN_TARGET_LIST) ]; then \
	cp -f $(DYN_TARGET) $(DESTDIR)$(PREFIX)/lib/$(DYN_TARGET_LIST); \
	fi
	ln -f -s lib$(TARGET_NAME).so.$(LIB_VER) $(DESTDIR)$(PREFIX)/lib/lib$(TARGET_NAME).so
	ln -f -s lib$(TARGET_NAME).so.$(LIB_VER) $(DESTDIR)$(PREFIX)/lib/lib$(TARGET_NAME).so.$(LIB_MAJOR_VER)
	ln -f -s lib$(TARGET_NAME).so.$(LIB_VER) $(DESTDIR)$(PREFIX)/lib/lib$(TARGET_NAME).so.$(LIB_MAJOR_VER).$(LIB_MINOR_VER)
endif
ifndef DYNAMIC_ONLY
	@if ! [ $(STATIC_TARGET) -ef $(DESTDIR)$(PREFIX)/lib/$(STATIC_TARGET_LIST) ]; then \
	cp -f $(STATIC_TARGET) $(DESTDIR)$(PREFIX)/lib/$(STATIC_TARGET_LIST); \
	fi
endif
	-cp -f $(API_HEADERS) $(DESTDIR)$(PREFIX)/include/$(TARGET_NAME)

deps: $(DEP_BUILD_LIST)
%.git:
	echo -e "\n TEENSY DEPENDENCIES: $(call branch,$@) @ $(call repo,$@) \n" \
        && echo "Calling $(PYTHON) $(PYTHON_SCRIPTS_DIR)/dependencies.py $(call repo,$@) $(call branch,$@)" \
	&& $(PYTHON) $(PYTHON_SCRIPTS_DIR)/dependencies.py $(DEPDIR) $(call repo,$@) $(call branch,$@) \
	&& cd $(DEPDIR)/$(call repo,$@) \
	&& git submodule init \
	&& git submodule update \
	&& cd $(CURDIR) \
	|| ( rm -Rf $(DEPDIR)/$(call repo,$@); exit 1 ); \
	make $(MAKECMDGOALS) -f $(MAKEFILE_NAME) -C $(DEPDIR)/$(call repo,$@) DESTDIR=$(DESTDIR) install || exit 1;

examples:
	$(foreach ex,$(EXAMPLE_DIRS), export DESTDIR=$(DESTDIR) && make -C $(ex) || exit 1;)

report_deps:
	$(PYTHON) $(PYTHON_SCRIPTS_DIR)/printVersionAll.py $(DEPDIR)

printvar:
	$(foreach v, $(.VARIABLES), $(info $(v) = $($(v))))

$(OBJDIR)%.o: $(SRCDIR)/%.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEFAULTFLAGS) -c -o $@ $<

$(OBJDIR)%.o: $(SRCDIR)/%.c
	$(CC) $(CPPFLAGS) $(CFLAGS) $(DEFAULTFLAGS) -c -o $@ $<

$(OBJDIR)%.o: $(SRCDIR)/%.S
	$(CC) $(CPPFLAGS) -x assembler-with-cpp $(DEFAULTFLAGS) -c -o $@ $<


# .PHONY prevent make from having issues with source files called all, profile, release, etc.
.PHONY : all profile release debug deb\
	install install-strip uninstall clean distclean veryclean directories symlinks set-install-local pkgconfig deps deb printvar examples \
	patches
