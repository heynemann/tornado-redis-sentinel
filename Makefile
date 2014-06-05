setup:
	@pip install -U -e .\[tests\]

test: redis_test unit

unit:
	@coverage run --branch `which nosetests` -vv --with-yanc -s tests/
	@coverage report -m --fail-under=80

coverage-html: unit
	@coverage html -d cover

kill_redis_test:
	-redis-cli -p 57575 shutdown
	-redis-cli -p 57576 shutdown
	-redis-cli -p 57577 shutdown
	-redis-cli -p 57574 shutdown

redis_test: kill_redis_test
	redis-sentinel ./redis_sentinel.conf; sleep 1
	redis-sentinel ./redis_sentinel2.conf; sleep 1
	redis-server ./redis_test.conf; sleep 1
	redis-server ./redis_test2.conf; sleep 1
	redis-server ./redis_test3.conf; sleep 1
	redis-cli -p 57574 info > /dev/null
