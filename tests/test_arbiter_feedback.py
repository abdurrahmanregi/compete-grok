import unittest
from agents.arbiter import create_arbiter_agent

class TestArbiterFeedback(unittest.TestCase):
    def test_create_arbiter_agent(self):
        """Test that the arbiter agent can be created without KeyError."""
        try:
            agent = create_arbiter_agent()
            self.assertIsNotNone(agent)
        except Exception as e:
            self.fail(f"Failed to create arbiter agent: {e}")

if __name__ == '__main__':
    unittest.main()
