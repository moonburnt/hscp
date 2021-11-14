# HSCP

## Description:

**HSCP** is a [HyScores](https://github.com/0x5b/hyscores) Client, written in 
Python. Its designed to be a simple and efficient library to use in your games.

## Usage:

```python3

from hscp import HyScoresClient

client = HyScoresClient(
    # replace this with url of actually running instance of HyScores
    url = "http://example.com",
    # and this with name of your application
    app = "hyscores",
)

# If you arent registered on this instance yet
client.register("your_login", "your_password") 

client.login("your_login", "your_password")

# This will get list of scores already uploaded to server
print(client.get_scores())
```

## License:

[MIT](https://github.com/moonburnt/hscp/blob/master/LICENSE)
