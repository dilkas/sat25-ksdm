TIMEOUT = 3600
MAX_DOMAIN_SIZE = 35

CRANE = /usr/bin/time -v java -jar target/scala-2.11/crane-assembly-1.0.jar -t $(TIMEOUT) -e $(MAX_DOMAIN_SIZE) --format-in mln

all: bijections/TARGET functions/TARGET

%/TARGET:
	-./forclift_wrapper.sh $(MAX_DOMAIN_SIZE) "../data/MLNs/functions/$*.mln" $(TIMEOUT) > results/$(subst /,_,$*).forclift 2>&1
	sed -i "s/\.\.\.,[[:digit:]]\+/\.\.\.,3/g" data/MLNs/functions/$*.mln
	-./fastwfomc_wrapper.sh $(MAX_DOMAIN_SIZE) "../data/JSON/$*.json" $(TIMEOUT) > results/$(subst /,_,$*).fastwfomc 2>&1
	-cd ../crane-dev && $(CRANE) "../practical-fomc/data/MLNs/functions/$*.mln" > ../practical-fomc/results/$(subst /,_,$*).greedy 2>&1
	-cd ../crane-dev && GREEDY=false $(CRANE) "../practical-fomc/data/MLNs/functions/$*.mln" > ../practical-fomc/results/$(subst /,_,$*).bfs 2>&1
