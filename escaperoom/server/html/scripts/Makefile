CC = coffee
SRC_DIR = src
OBJ = $(notdir $(subst .coffee,.mjs,$(wildcard $(SRC_DIR)/*.coffee)))

%.mjs: $(SRC_DIR)/%.coffee
	$(CC) -o $@ -c $<

all: $(OBJ)
