import asyncio
import io
import unittest
from contextlib import redirect_stdout

# Import the main() function from your CLI module.
# Adjust the import path as needed.
from conexia.cli import main

class TestCLI(unittest.TestCase):
    def test_cli_output(self):
        """Test that CLI prints expected output."""
        captured_output = io.StringIO()
        # Redirect stdout to capture prints from the main() function.
        with redirect_stdout(captured_output):
            asyncio.run(main())
        output = captured_output.getvalue()
        
        # Assert that output contains the expected keys.
        self.assertIn("User ID:", output)
        self.assertIn("Public IP:", output)
        self.assertIn("Public Port:", output)
        self.assertIn("NAT Type:", output)

if __name__ == '__main__':
    unittest.main()