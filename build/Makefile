TIMEOUT = 3600
MAX_MEMORY_KB = 177419059

CRANE = /usr/bin/time -v java -jar target/scala-2.11/crane-assembly-1.0.jar -t $(TIMEOUT) -d 0 --format-in mln

all: bijections/TARGET friends/TARGET functions/TARGET

%/TARGET:
	-./forclift_wrapper.sh "../../data/MLNs/$*.mln" $(TIMEOUT) $(MAX_MEMORY_KB) > ../results/raw/$(subst /,_,$*).forclift 2>&1
	sed -i "s/\.\.\.,[[:digit:]]\+/\.\.\.,3/g" ../data/MLNs/$*.mln
	-./fastwfomc_wrapper.sh "../data/JSON/$*.json" $(TIMEOUT) $(MAX_MEMORY_KB) > ../results/raw/$(subst /,_,$*).fastwfomc 2>&1
	-cd ../../gantry && ulimit -c 0 -Sv $(MAX_MEMORY_KB) && $(CRANE) "../practical-fomc/data/MLNs/$*.mln" > ../practical-fomc/results/raw/$(subst /,_,$*).greedy 2>&1
	-cd ../../gantry && ulimit -c 0 -Sv $(MAX_MEMORY_KB) && GREEDY=false $(CRANE) "../practical-fomc/data/MLNs/$*.mln" > ../practical-fomc/results/raw/$(subst /,_,$*).bfs 2>&1
