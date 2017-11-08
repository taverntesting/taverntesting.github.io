#!/usr/bin/env python

import pypandoc

rst = pypandoc.convert_file("index.md", "rst")

with open("README.rst", "w") as rstfile:
    rstfile.write(rst)
