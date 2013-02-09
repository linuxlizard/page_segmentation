# Run segmentation on missing images
# davep 8-Feb-2013

INPUT=$(notdir $(shell ls -d 300/[W]???ZONE))
#INPUT=$(notdir $(shell ls -d 300/????ZONE))

#OUTPUT=$(foreach fname,$(INPUT),300_rast/$(fname)/$(fname).dat)
OUTPUT=$(foreach fname,$(INPUT),300_vor/$(fname)/$(fname).dat)

#ALGO=rast
ALGO=voronoi

all : $(OUTPUT)

# @echo is for debugging; remove when running
$(OUTPUT) :
#@echo python runseg.py --docid $(basename $(notdir $@)) --seg $(ALGO)
	python runseg.py --docid $(basename $(notdir $@)) --seg $(ALGO)

