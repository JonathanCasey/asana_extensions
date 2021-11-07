#!/usr/bin/env python3
"""
The main entry point for the package when running as a module.

This is kept to a bare minimum -- basically a wrapper call to the real main.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from asana_extensions import main



if __name__ == '__main__':                                  # Ignored by CodeCov
    # Since no unit testing here, code kept at absolute minimum
    main._setup_and_call_main()               # pylint: disable=protected-access
