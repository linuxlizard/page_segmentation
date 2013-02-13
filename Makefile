# Run segmentation on missing images
# davep 8-Feb-2013

#SIZE=300
SIZE=600

#ALGO=rast
ALGO=vor

INPUT=$(notdir $(shell ls -d $(SIZE)/[A-V]???ZONE))
#INPUT=$(notdir $(shell ls -d $(SIZE)/[W]???ZONE))

# output should look e.g., 600_rast/A001ZONE/A001ZONE.dat
OUTPUT=$(foreach fname,$(INPUT),$(SIZE)_$(ALGO)/$(fname)/$(fname).dat)

# @echo is for debugging; remove when running
DEBUG=@echo
#DEBUG=

ifeq ($(ALGO),rast)
SEGMENTATION=rast
else
SEGMENTATION=voronoi
endif

#ALGO=rast
#ALGO=voronoi

all : $(OUTPUT)

$(OUTPUT) :
	$(DEBUG) python runseg.py --docid $(basename $(notdir $@)) --seg $(SEGMENTATION)

