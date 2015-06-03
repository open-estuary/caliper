LOCAL_PATH := $(call my-dir)/..

include $(CLEAR_VARS)
LOCAL_MODULE := cachebench
LOCAL_SRC_FILES := cachebench.c
LOCAL_CFLAGS := -O2 -mcpu=cortex-a15 -mfpu=neon-vfpv4 -UNDEBUG
#LOCAL_CFLAGS := -O2
LOCAL_LDLIBS := -lc -lm
#TARGET_CFLAGS := $(filter-out -march=armv7-a, $(TARGET_CFLAGS))
#TARGET_CFLAGS := $(filter-out -mfpu=vfpv3-d16, $(TARGET_CFLAGS))
LOCAL_ARM_MODE := arm
include $(BUILD_EXECUTABLE)
