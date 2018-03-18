#!/bin/bash
set -ex

VERSION=$(git describe)

build_image() {
    docker build --build-arg APP_VERSION="$VERSION" -t "$DOCKER_USERNAME/energy-logger-ui:$VERSION" .
}

if [ "$TRAVIS_PULL_REQUEST" != "false" ]; then
    # PR build
    build_image
else
    # Release build
    build_image

    if [ ! -z "$TRAVIS_TAG" ]; then
        echo "Publishing image to Docker hub..."
        docker login -u "$DOCKER_USERNAME" -p "$DOCKER_PASSWORD"
        docker push "$DOCKER_USERNAME/energy-logger-ui:$VERSION"
    fi
fi
