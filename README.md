# SĘP
<img src="https://thumbs.dreamstime.com/b/%C5%9Bliczny-s%C4%99p-12553165.jpg" alt="drawing" width="200"/>

Semantic Evaluation Platform 

[![Build Status](https://travis-ci.com/Fafa87/SEP.svg?branch=master)](https://travis-ci.com/Fafa87/SEP)
[![GitHub release](https://img.shields.io/github/release/Fafa87/SEP.svg)](https://GitHub.com/Fafa87/SEP/releases/)

[![PyPI version](https://img.shields.io/pypi/v/semevalplatform.svg)](https://pypi.org/project/semevalplatform/)
[![PyPi](https://img.shields.io/pypi/pyversions/semevalplatform)](https://pypi.org/project/semevalplatform/)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20osx%20%7C%20ubuntu-lightgrey)

Deserve the money! - ML engineers are paid a lot of money however most of the time is spent on common tasks and debuging standard problems. This is an attempt to help with that.

## Description

Platform designed to speed up working o the computer vision tasks (especially semantic segmentation) by providing commonly used functions and utilities so that you can concentrate more on designing solution than reimplementing basics. This is generic pure Python designed to work well with jupyter.

The platform can be used in many ways, from complete integration to just using a few utility classes or methods (e.g. loading data).
 
## Abilities

This includes:
- Dataset loading and gathering (never again start a project with `glob`), easily work with movies and even extract frames from youtube!
- Dataset inspection (quickly check and recheck) input images and annotations consistency, tag images and group them. Also remove images that are hurting your solution or evaluation.
- Visualisation tools (based on jupyter and napari). Methods to create a few simple visualization of ground truth and results.
- Evaluation scheme (no need to set it up again - just implement `Producer`, choose metrics and regions of interest), get multilevel evaluation of the solution.
- Annotation verification...
- Visual comparison on not annotated data...
- And even more!

## Main actors

Loader...
Inspector...
Tagger...

## Installation

`pip install semevalplatform`

if you are interested in using `napari` based gui you have to install `napari` and `magicgui` (preferably using conda so that you get `qt` in the package).

## Examples
- grr - virtual green screen
- grr - physical green screen 
- msee - foreground separation