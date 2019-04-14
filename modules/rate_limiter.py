from time import time, sleep


class DownloadRateLimiter():
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.start = time()

        
    def __call__(self, block_count, block_size, total_size):
        total_kb = total_size / 1024
        downloaded_kb = (block_count * block_size) / 1024
        elapsed_time = time() - self.start
        if elapsed_time != 0:
            rate = downloaded_kb / elapsed_time
            expected_time = downloaded_kb / self.rate_limit
            sleep_time = expected_time - elapsed_time
            if sleep_time:
                sleep(sleep_time)

