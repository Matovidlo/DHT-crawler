#!/usr/bin/env bats

@test "Simple connection test" {
	run ../src/monitor.py --test
	[ "$status" -eq 2 ]
}
