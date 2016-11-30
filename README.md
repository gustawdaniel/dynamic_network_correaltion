# Dynamic Stock Network Visualisation

Script allows to visualise correlation network of companies from stock market.

## Instalation

After cloning repository and `cd` into these directory run:

    bash install.sh

This script installs dependencies, download data and prepare them to test. In new terminal open `ubigraph_server`:

    ubigraph_server

Run `visualise.py` script:

    python visualise.py

and type the following input:

```
test ENTER ENTER ENTER ENTER ENTER
```

You should see on screen of `ubigraph_server` visualisation like this

![Visualisation](http://i.imgur.com/UAgE9to.png)

Look at video

+ [1](https://vid.me/e/I6nt)
+ [2](https://vid.me/e/Bwzr)

### Dependencies

    sudo apt-get install freeglut3-dev
    sudo apt-get install jq

### Source of data

> http://bossa.pl/pub/