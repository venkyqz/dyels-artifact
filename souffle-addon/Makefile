KECCAK_DIR := keccak
KECCAK_SRC := $(wildcard $(KECCAK_DIR)/*.c)
KECCAK_OBJ := $(patsubst $(KECCAK_DIR)/%.c,$(KECCAK_DIR)/%.o, $(KECCAK_SRC))
WORD_SIZE=32

.PHONY: clean softclean

# rudimentary
all: libsoufflenum.so

libsoufflenum.so: $(KECCAK_OBJ) num256.o mappings.o keccak256.o lists.o smt-api.o hashsum_functor.o lub_functor.o fold_functor.o
	g++ -std=c++17 -shared -o libsoufflenum.so $(KECCAK_OBJ) smt-api.o num256.o mappings.o keccak256.o lists.o hashsum_functor.o lub_functor.o fold_functor.o -march=native -lz3 -fopenmp -DRAM_DOMAIN_SIZE=$(WORD_SIZE)
	ln -sf libsoufflenum.so libfunctors.so

hashsum_functor.o: hashsum_functor.cpp
	g++ -std=c++17 hashsum_functor.cpp -lz3 -fopenmp -DRAM_DOMAIN_SIZE=$(WORD_SIZE) -c -fPIC -o hashsum_functor.o

fold_functor.o: fold_functor.cpp
	g++ -std=c++17 fold_functor.cpp -lz3 -fopenmp -DRAM_DOMAIN_SIZE=$(WORD_SIZE) -c -fPIC -o fold_functor.o

lub_functor.o: lub_functor.cpp
	g++ -std=c++17 lub_functor.cpp -lz3 -fopenmp -DRAM_DOMAIN_SIZE=$(WORD_SIZE) -c -fPIC -o lub_functor.o

smt-api.o: smt-api.cpp
	g++ -std=c++17 smt-api.cpp -lz3 -fopenmp -DRAM_DOMAIN_SIZE=$(WORD_SIZE) -c -fPIC -o smt-api.o

num256.o: num256.cpp
	g++ -std=c++17 -O2 num256.cpp -c -fPIC -o num256.o -lz3 -fopenmp

mappings.o: mappings.cpp
	g++ -std=c++17 -O2 mappings.cpp -c -fPIC -o mappings.o -lz3 -fopenmp

lists.o: lists.cpp
	g++ -std=c++17 -O2 lists.cpp -c -fPIC -o lists.o -lz3 -fopenmp -DRAM_DOMAIN_SIZE=$(WORD_SIZE)

keccak256.o: keccak256.cpp
	g++ -std=c++17 -O2 keccak256.cpp -c -fPIC -o keccak256.o -fopenmp

$(KECCAK_DIR)/%.o: $(KECCAK_DIR)/%.c $(KECCAK_SRC)
	gcc -O2 -fopenmp -c -fPIC -o $@ $<

softclean:
	rm -f $(KECCAK_OBJ)
	rm -f *.o

clean: softclean
	rm -f libsoufflenum.so libfunctors.so
