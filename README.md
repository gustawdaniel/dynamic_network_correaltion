# Dynamic Stock Network Visualisation

Script allow to visualise correlation network of companies from stock market.

<iframe src="https://vid.me/e/I6nt?autoplay=0&amp;loop=1&amp;muted=1&amp;stats=1" width="854" height="480" frameborder="0" allowfullscreen webkitallowfullscreen mozallowfullscreen scrolling="no"></iframe>

<iframe src="https://vid.me/e/Bwzr?autoplay=0&amp;loop=1&amp;muted=1&amp;stats=1" width="854" height="480" frameborder="0" allowfullscreen webkitallowfullscreen mozallowfullscreen scrolling="no"></iframe>

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

### Dependencies

    sudo apt-get install freeglut3-dev
    sudo apt-get install jq

### Source of data

> http://bossa.pl/pub/