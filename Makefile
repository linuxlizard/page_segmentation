
INPUT=$(notdir $(shell ls -d 300/[A-V]???ZONE))
#INPUT=$(notdir $(shell ls -d 300/????ZONE))

OUTPUT=$(foreach fname,$(INPUT),300_rast/$(fname)/$(fname).dat)

all : $(OUTPUT)

$(OUTPUT) :
	@echo python runseg.py $(basename $(notdir $@)) 

