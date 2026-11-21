#!/bin/sh
# Wraps src/game.html in a document shell so index.html opens directly in a browser.
{
  printf '%s\n' '<!doctype html>' '<html lang="en">' '<meta charset="utf-8">' '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">'
  cat src/game.html
} > index.html
