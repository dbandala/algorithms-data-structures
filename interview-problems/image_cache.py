# Laptop problem - Image Cache
# You are to build a simple image cache for holding images in memory. The cache should have a maximum size in bytes. Since the cache has a limited byte size, we will use an LRU (Least Recently Used) policy to evict images from the cache when the cache is full

# The format of the input file will be as follows:
# The first line will contain a single integer n, where n is the maximum size of the cache in bytes
# The second line will be an integer that indicates the number of URLs that will appear subsequently in the input file
# The next n lines will contain the URLs of the images that are requested by the user. The URLs will be in the format of a string

# For each URL, your program should attempt to fetch it from the cache, and if it isn't present, download it from the internet and place it in the cache. You should save the entire image in the cache, event though you can achieve the desired output without doing so

# Your output should contain N lines, in the same order as the input. Each line will be formatted as follows:
# <url requested> <in_cache|downloaded> <size of image in bytes>

import requests
from lru import LRU


class ImageCache:
    def __init__(self, max_size):
        self.cache = LRU(max_size//100) # {}
        self.size = 0 # size of the cache in bytes
        self.max_size = max_size # maximum size of the cache in bytes
    
    # method to fetch image from cache
    def fetch_image(self, url):
        if url in self.cache:
            return self.cache[url]
        else:
            return self.download_image(url)
    
    # method to download image from internet
    def download_image(self, url):
        # Download the image from the internet
        img_data = requests.get(url).content
        # Check if the image can fit in the cache
        if len(img_data) > self.max_size:
            return "Image too large"
        # Save the image in the cache
        self.cache[url] = img_data
        self.size += len(img_data)
        # return image
        return img_data
    


# Test cases
if __name__ == "__main__":
    cache = ImageCache()
    print(cache.fetch_image("https://www.google.com"))
    print(cache.download_image("https://www.google.com"))


