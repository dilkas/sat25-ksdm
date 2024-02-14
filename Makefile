TIMEOUT = 60
MAX_MEMORY_KB = 33554432
MAX_DOMAIN_SIZE = 10

RUN = cd ../crane-dev && ulimit -Sv $(MAX_MEMORY_KB) &&
CRANE = /usr/bin/time -v java -jar target/scala-2.11/crane-assembly-1.0.jar -t $(TIMEOUT) -e $(MAX_DOMAIN_SIZE) --format-in mln

all: $(addsuffix /TARGET,$(wildcard data/sequences/a*.mln))
clean: $(addsuffix /CLEAN,$(wildcard data/sequences/a*.mln))

data/sequences/%.mln/TARGET:
	-ulimit -Sv $(MAX_MEMORY_KB) && ./forclift_wrapper.sh $(MAX_DOMAIN_SIZE) "../data/sequences/$*.mln" $(TIMEOUT) > results/$(subst /,_,$*).forclift 2>&1
	sed -i "s/\.\.\.,[[:digit:]]\+/\.\.\.,3/g" data/sequences/$*.mln
	-$(RUN) $(CRANE) "../practical-fomc/data/sequences/$*.mln" > ../practical-fomc/results/$(subst /,_,$*).greedy 2>&1
	-$(RUN) GREEDY=false $(CRANE) "../practical-fomc/data/sequences/$*.mln" > ../practical-fomc/results/$(subst /,_,$*).bfs 2>&1

data/sequences/%.mln/CLEAN:
	sed -i "s/\.\.\.,[[:digit:]]\+/\.\.\.,3/g" data/sequences/$*.mln
