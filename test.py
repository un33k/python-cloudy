import unittest
import sys
import logging

class TestCloudyFunctions(unittest.TestCase):

    def setUp(self):
        self.log= logging.getLogger( "TestCloudyFunctions" )


    def test_manager(self):
        pass

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "TestCloudyFunctions" ).setLevel( logging.DEBUG )
    unittest.main()


