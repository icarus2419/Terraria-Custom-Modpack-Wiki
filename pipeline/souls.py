"""The two Soul sprites, embedded.

The theme toggle is the pair of items the palette is sampled from -- Soul of Light for the
light theme, Soul of Night for the dark one -- so the control shows you the thing it does
rather than a sun-and-moon glyph that could mean anything.

Both are the wiki's own animated GIFs, four frames each, which is where the toggle's flicker
comes from: no CSS, just the sprite doing what it does in-game. Embedded rather than fetched,
like every other sprite on this site, so the page still works with no network.
"""

SOUL = {
  "light": "data:image/gif;base64,R0lGODlhFgAWAMIHAHsATqkbfdwdt+pf0v9sxv+N0//U7////yH/C05FVFNDQVBFMi4wAwEAAAAh+QQJCgAHACwAAAAAFgAWAAADbni6IvswqiYrE6XQBYA9TbYpXRUWhiEKXVNCZ7q2rCed4/GamOZwtkggMKl1dofhQwkyHpfEZIBAYNJeQ+owW41ebVwmk3SkKcbSR9mcliBxv8q7l1MDXPeezBf5xlR8bkFNKx9zhR83cYkRdQcJACH5BAkKAAcALAAAAAAWABYAAANveLqsIi1KB6d9pTwrsa5TEFCZYWSbJJKFiYKLSBDr4aUAwMj0aAsvRS5Sy4lwgMcw5jMGkErdYang1YRS7C4wu06luShFtPSGBcsHWerV/oIHq899q8gjHtenOm/kT3txfXhAgRwMdYcdMIqIjBIJACH5BAkKAAcALAAAAAAWABYAAAOBeLocwTBCJ+tyhNAjhL1BtnUVADQPJxQFCZmo0rGuYnam48yFYdCew02Q0/F8QEZxMGAxebXFsll4rlpBRsfBQhZ2Wcg20P19A1HZtcN0Dhww8VrQrr4DcXUZqMMDcCcqe1h9Q3mCWAobNoFac4opjBUuGBqRFpQhlh8Vi5wRnhEJACH5BAkKAAcALAAAAAAWABYAAANweLoKwDBCJ+tyQtATgr1AtnVf1jxcQBCkZB6jynpQVhQv00Y2LkS7Rc9guGU6m9xhWPQhUUpF7yjrTH9CgVHQWVm1Ph7W8b0Rt4wXOcBEQ4JScHQBX8qxuiotiX/rT3EfLRgaKIJ7IYUfFRuLEo0QCQA7",
  "night": "data:image/gif;base64,R0lGODlhFgAWAMIHAD8Ae1cbqXsd3KJf6rxs/+CN//3U/////yH/C05FVFNDQVBFMi4wAwEAAAAh+QQJCgAHACwAAAAAFgAWAAADfXi607MwSvekVa0UY9qdg8Z5nyIIWlqQQAtIp6qxLixkxQm1ZwudON2CJ/AdAsjAqecytpJQ5bLpBEQDBAJSQTQis1BwgAtgKr7aaLW5FFyRa1cbSjYvYquBsF583VF5e0M1BzgqgmRGhimIFg0cMxUlGAOQeZMRFJggJBAJACH5BAkKAAcALAAAAAAWABYAAAODeHrRITCuSd2LkNZASIPDUBShpjTdJ4RjaQKACo00OWiwLNTtvcAQ2GRWMBhcCqBAuCAakT/AJBcIQafSaMPqM21SAa8X5QmLJ9wGM5nVpAPrQ1wRMo4y0WD7UDfcBVh6aCI8GGp7dIQ1hnCICyw2EGQNXpAhkhxlZxiYlGcHnAIWEwkAIfkECQoABwAsAAAAABYAFgAAA4V4uhr+LMrz4JQAOEKc+MKlZFsXgOGUfeQpDENRwBjAai4s01HWegKZcDZg+HDA4a4YceiIH5nBwGM4Y9BgYcqDwRxSg+xaPXgH4K24QGbCprLP8xuQvNdyLN2OHX4qRwxPfgKAPnxLfwErAhmIWQ6MjhMoJZEAIgeVARyXmVYVdZ+gFRcJACH5BAkKAAcALAAAAAAWABYAAAN+eLrMAC1K9aY9T4gXwnWAxnnNYA7RSBAdc6KNypJmURiGGWlde9S3HIzB62lsyIKpUzlons+kbRloQqHA4qpzVA6wA5t21jVdnxRAB5g8a9LrsLTIFURMuCmsF3iXBnleCh1bVRB/OguEM00uJxFMIRuHHweRIpSVC42aIJ0JADs=",
}

def img(which, size=16, cls=""):
    return ('<img class="%s" src="%s" width="%d" height="%d" alt="" aria-hidden="true" '
            'decoding="async">' % (cls, SOUL[which], size, size))
