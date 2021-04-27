# RedisBloomCMSTester
test script to check the accuracy of Count-Min Sketches in RedisBloom

## Redis Instance

### Start a Redis Instance Running the RedisBloom Module

Warning: will run in the foreground and block the terminal you run it in.

```bash
docker run -p 6379:6379 --name redis-redisbloom redislabs/rebloom:latest
```

### Connect to the Redis Instance

In a different terminal (with the instance running elsewhere):
```bash
redis-cli
```

Note: if you use a port other than 6379 or run your Redis instance on a computer other than the one you're running `redis-cli` on, you'll have to supply those as parameters to connect. We're just lazily relaying on the CLI's default ip of 127.0.0.1 and the default port of 6379 here.

### Initialize a Count-Min Sketch

In the Redis CLI:
```bash
CMS.INITBYDIM testCMS 300 4
```

## Script
### Install the RedisBloom Python Driver

In yet another terminal:

```bash
pip3 install redisbloom
```

### Run the Script

```bash
python3 websiteVisitorsSimulation.py -numVisitors 400 -numVisits 10000 -compare true -cmsName testCMS -numToCompare 20
```
