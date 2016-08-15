#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oerweekapi.settings")

    # we're using pytest so treat tests as special
    if 'test' in sys.argv:
        import pytest
        # We need to remove "test" so that pytest picks up additional args only
        sys.argv.pop(1)
        sys.exit(pytest.main())
    else:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
    #
