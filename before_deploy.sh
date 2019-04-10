#!/usr/bin/env bash

if [[ "$TRAVIS_TAG" =~ tdvt ]]; then
    echo tdvt
elif [[ "$TRAVIS_TAG" =~ packaging ]]; then
    echo packaging
fi
